odoo.define('pos_member_type.Loyalty', function(require) {
    'use strict';

    const {Order} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');


    const PosLoyaltyOrderExt = (Order) => class PosLoyaltyOrderExt extends Order {
        pointsForPrograms(programs) {
        console.log('pointsForPrograms');
            const totalTaxed = this.get_total_with_tax();
            const totalUntaxed = this.get_total_without_tax();
            const totalsPerProgram = Object.fromEntries(programs.map((program) => [program.id, {'untaxed': totalUntaxed, 'taxed': totalTaxed}]));
            const orderLines = this.get_orderlines();
            console.log('orderlines',this.get_orderlines());
            for (const line of orderLines) {
                if (!line.reward_id) {
                    continue;
                }
                const reward = this.pos.reward_by_id[line.reward_id];
                console.log('reward',reward);
                if (reward.reward_type !== 'discount') {
                    continue;
                }
                const rewardProgram = reward.program_id;
                for (const program of programs) {
                    // Remove automatic discount and this program's discounts from the totals.
                    if (program.id === rewardProgram.id || rewardProgram.trigger === 'auto') {
                        totalsPerProgram[program.id]['taxed'] -= line.get_price_with_tax();
                        totalsPerProgram[program.id]['untaxed'] -= line.get_price_without_tax();
                    }
                }
            }
            const result = {}
            const customer = this.pos.get_order().partner;
            for (const program of programs) {
                let points = 0;
                const splitPoints = [];
                console.log('partner',customer);
                console.log('program',program)
                if (customer){
                    console.log('has Customer');
                    if (customer.pos_member_type_id){
                        console.log('has customer.pos_member_type_id');
                        if (customer.pos_member_type_id[0] === program.pos_member_type_id[0]){
                        console.log('same pos_member_type_id');
                            for (const rule of program.rules) {
                                console.log('program.rules',rule);
                                if (rule.mode === 'with_code' && !this.codeActivatedProgramRules.includes(rule.id)) {
                                    continue;
                                }
                                const amountCheck = rule.minimum_amount_tax_mode === 'incl' && totalsPerProgram[program.id]['taxed'] || totalsPerProgram[program.id]['untaxed'];
                                if (rule.minimum_amount > amountCheck) { // NOTE: big doutes par rapport au fait de compter tous les produits
                                console.log('minimum amount',rule.minimum_amount);
                                console.log('amountCheck',amountCheck);
                                    continue;
                                }
                                let totalProductQty = 0;
                                // Only count points for paid lines.
                                const qtyPerProduct = {};
                                let orderedProductPaid = 0;
                                for (const line of orderLines) {
                                    if (((!line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.get_product().id))) ||
                                        (line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.reward_product_id)))) &&
                                        !line.ignoreLoyaltyPoints({ program })){
                                        // We only count reward products from the same program to avoid unwanted feedback loops
                                        if (line.reward_product_id) {
                                            const reward = this.pos.reward_by_id[line.reward_id];
                                            if (program.id !== reward.program_id) {
                                                continue;
                                            }
                                        }
                                        const lineQty = (line.reward_product_id ? -line.get_quantity() : line.get_quantity());
                                        totalProductQty += lineQty;
                                        if (qtyPerProduct[line.reward_product_id || line.get_product().id]) {
                                            qtyPerProduct[line.reward_product_id || line.get_product().id] += lineQty;
                                        } else {
                                            qtyPerProduct[line.reward_product_id || line.get_product().id] = lineQty;
                                        }
                                        orderedProductPaid += line.get_price_with_tax();
                                    }
                                }
                                if (totalProductQty < rule.minimum_qty) {
                                    // Should also count the points from negative quantities.
                                    // For example, when refunding an ewallet payment. See TicketScreen override in this addon.
                                    continue;
                                }
                                if (program.applies_on === 'future' && rule.reward_point_split && rule.reward_point_mode !== 'order') {
                                    // In this case we count the points per rule
                                    if (rule.reward_point_mode === 'unit') {
                                        splitPoints.push(...Array.apply(null, Array(totalProductQty)).map((_) => {return {points: rule.reward_point_amount}}));
                                    } else if (rule.reward_point_mode === 'money') {
                                        for (const line of orderLines) {
                                            if (line.is_reward_line || !(rule.valid_product_ids.has(line.get_product().id)) || line.get_quantity() <= 0
                                                || line.ignoreLoyaltyPoints({ program })) {
                                                continue;
                                            }
                                            let price_to_use = line.get_price_with_tax();
                                            if (program.program_type === 'gift_card') {
                                                price_to_use = line.price;
                                            }
                                            const pointsPerUnit = round_precision(rule.reward_point_amount * price_to_use / line.get_quantity(), 0.01);
                                            if (pointsPerUnit > 0) {
                                                splitPoints.push(...Array.apply(null, Array(line.get_quantity())).map(() => {
                                                    if (line.giftBarcode && line.get_quantity() == 1) {
                                                        return {points: pointsPerUnit, barcode: line.giftBarcode, giftCardId: line.giftCardId };
                                                    }
                                                    return {points: pointsPerUnit}
                                                }));
                                            }
                                        }
                                    }
                                } else {
                                    // In this case we add on to the global point count
                                    if (rule.reward_point_mode === 'order') {
                                        points += rule.reward_point_amount;
                                    } else if (rule.reward_point_mode === 'money') {
                                        // NOTE: unlike in sale_loyalty this performs a round half-up instead of round down
                                        points += round_precision(rule.reward_point_amount * orderedProductPaid, 0.01);
                                    } else if (rule.reward_point_mode === 'unit') {
                                        points += rule.reward_point_amount * totalProductQty;
                                    }
                                }
                            }
                        }
                    }else{
                        console.log('does not have customer.pos_member_type_id');
                        if (!program.pos_member_type_id){
                            for (const rule of program.rules) {
                                console.log('program.rules',rule);
                                if (rule.mode === 'with_code' && !this.codeActivatedProgramRules.includes(rule.id)) {
                                    continue;
                                }
                                const amountCheck = rule.minimum_amount_tax_mode === 'incl' && totalsPerProgram[program.id]['taxed'] || totalsPerProgram[program.id]['untaxed'];
                                if (rule.minimum_amount > amountCheck) { // NOTE: big doutes par rapport au fait de compter tous les produits
                                console.log('minimum amount',rule.minimum_amount);
                                console.log('amountCheck',amountCheck);
                                    continue;
                                }
                                let totalProductQty = 0;
                                // Only count points for paid lines.
                                const qtyPerProduct = {};
                                let orderedProductPaid = 0;
                                for (const line of orderLines) {
                                    if (((!line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.get_product().id))) ||
                                        (line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.reward_product_id)))) &&
                                        !line.ignoreLoyaltyPoints({ program })){
                                        // We only count reward products from the same program to avoid unwanted feedback loops
                                        if (line.reward_product_id) {
                                            const reward = this.pos.reward_by_id[line.reward_id];
                                            if (program.id !== reward.program_id) {
                                                continue;
                                            }
                                        }
                                        const lineQty = (line.reward_product_id ? -line.get_quantity() : line.get_quantity());
                                        totalProductQty += lineQty;
                                        if (qtyPerProduct[line.reward_product_id || line.get_product().id]) {
                                            qtyPerProduct[line.reward_product_id || line.get_product().id] += lineQty;
                                        } else {
                                            qtyPerProduct[line.reward_product_id || line.get_product().id] = lineQty;
                                        }
                                        orderedProductPaid += line.get_price_with_tax();
                                    }
                                }
                                if (totalProductQty < rule.minimum_qty) {
                                    // Should also count the points from negative quantities.
                                    // For example, when refunding an ewallet payment. See TicketScreen override in this addon.
                                    continue;
                                }
                                if (program.applies_on === 'future' && rule.reward_point_split && rule.reward_point_mode !== 'order') {
                                    // In this case we count the points per rule
                                    if (rule.reward_point_mode === 'unit') {
                                        splitPoints.push(...Array.apply(null, Array(totalProductQty)).map((_) => {return {points: rule.reward_point_amount}}));
                                    } else if (rule.reward_point_mode === 'money') {
                                        for (const line of orderLines) {
                                            if (line.is_reward_line || !(rule.valid_product_ids.has(line.get_product().id)) || line.get_quantity() <= 0
                                                || line.ignoreLoyaltyPoints({ program })) {
                                                continue;
                                            }
                                            let price_to_use = line.get_price_with_tax();
                                            if (program.program_type === 'gift_card') {
                                                price_to_use = line.price;
                                            }
                                            const pointsPerUnit = round_precision(rule.reward_point_amount * price_to_use / line.get_quantity(), 0.01);
                                            if (pointsPerUnit > 0) {
                                                splitPoints.push(...Array.apply(null, Array(line.get_quantity())).map(() => {
                                                    if (line.giftBarcode && line.get_quantity() == 1) {
                                                        return {points: pointsPerUnit, barcode: line.giftBarcode, giftCardId: line.giftCardId };
                                                    }
                                                    return {points: pointsPerUnit}
                                                }));
                                            }
                                        }
                                    }
                                } else {
                                    // In this case we add on to the global point count
                                    if (rule.reward_point_mode === 'order') {
                                        points += rule.reward_point_amount;
                                    } else if (rule.reward_point_mode === 'money') {
                                        // NOTE: unlike in sale_loyalty this performs a round half-up instead of round down
                                        points += round_precision(rule.reward_point_amount * orderedProductPaid, 0.01);
                                    } else if (rule.reward_point_mode === 'unit') {
                                        points += rule.reward_point_amount * totalProductQty;
                                    }
                                }
                            }
                        }
                    }
                }else{
                console.log('Do not choose customer')
                    if (!program.pos_member_type_id){
                        for (const rule of program.rules) {
                            console.log('program.rules',rule);
                            if (rule.mode === 'with_code' && !this.codeActivatedProgramRules.includes(rule.id)) {
                                continue;
                            }
                            const amountCheck = rule.minimum_amount_tax_mode === 'incl' && totalsPerProgram[program.id]['taxed'] || totalsPerProgram[program.id]['untaxed'];
                            if (rule.minimum_amount > amountCheck) { // NOTE: big doutes par rapport au fait de compter tous les produits
                            console.log('minimum amount',rule.minimum_amount);
                            console.log('amountCheck',amountCheck);
                                continue;
                            }
                            let totalProductQty = 0;
                            // Only count points for paid lines.
                            const qtyPerProduct = {};
                            let orderedProductPaid = 0;
                            for (const line of orderLines) {
                                if (((!line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.get_product().id))) ||
                                    (line.reward_product_id && (rule.any_product || rule.valid_product_ids.has(line.reward_product_id)))) &&
                                    !line.ignoreLoyaltyPoints({ program })){
                                    // We only count reward products from the same program to avoid unwanted feedback loops
                                    if (line.reward_product_id) {
                                        const reward = this.pos.reward_by_id[line.reward_id];
                                        if (program.id !== reward.program_id) {
                                            continue;
                                        }
                                    }
                                    const lineQty = (line.reward_product_id ? -line.get_quantity() : line.get_quantity());
                                    totalProductQty += lineQty;
                                    if (qtyPerProduct[line.reward_product_id || line.get_product().id]) {
                                        qtyPerProduct[line.reward_product_id || line.get_product().id] += lineQty;
                                    } else {
                                        qtyPerProduct[line.reward_product_id || line.get_product().id] = lineQty;
                                    }
                                    orderedProductPaid += line.get_price_with_tax();
                                }
                            }
                            if (totalProductQty < rule.minimum_qty) {
                                // Should also count the points from negative quantities.
                                // For example, when refunding an ewallet payment. See TicketScreen override in this addon.
                                continue;
                            }
                            if (program.applies_on === 'future' && rule.reward_point_split && rule.reward_point_mode !== 'order') {
                                // In this case we count the points per rule
                                if (rule.reward_point_mode === 'unit') {
                                    splitPoints.push(...Array.apply(null, Array(totalProductQty)).map((_) => {return {points: rule.reward_point_amount}}));
                                } else if (rule.reward_point_mode === 'money') {
                                    for (const line of orderLines) {
                                        if (line.is_reward_line || !(rule.valid_product_ids.has(line.get_product().id)) || line.get_quantity() <= 0
                                            || line.ignoreLoyaltyPoints({ program })) {
                                            continue;
                                        }
                                        let price_to_use = line.get_price_with_tax();
                                        if (program.program_type === 'gift_card') {
                                            price_to_use = line.price;
                                        }
                                        const pointsPerUnit = round_precision(rule.reward_point_amount * price_to_use / line.get_quantity(), 0.01);
                                        if (pointsPerUnit > 0) {
                                            splitPoints.push(...Array.apply(null, Array(line.get_quantity())).map(() => {
                                                if (line.giftBarcode && line.get_quantity() == 1) {
                                                    return {points: pointsPerUnit, barcode: line.giftBarcode, giftCardId: line.giftCardId };
                                                }
                                                return {points: pointsPerUnit}
                                            }));
                                        }
                                    }
                                }
                            } else {
                                // In this case we add on to the global point count
                                if (rule.reward_point_mode === 'order') {
                                    points += rule.reward_point_amount;
                                } else if (rule.reward_point_mode === 'money') {
                                    // NOTE: unlike in sale_loyalty this performs a round half-up instead of round down
                                    points += round_precision(rule.reward_point_amount * orderedProductPaid, 0.01);
                                } else if (rule.reward_point_mode === 'unit') {
                                    points += rule.reward_point_amount * totalProductQty;
                                }
                            }
                        }
                    }
                }
                const res = points ? [{points}] : [];
                if (splitPoints.length) {
                    res.push(...splitPoints);
                }
                result[program.id] = res;
            }
            return result;
        }
    }



    Registries.Model.extend(Order, PosLoyaltyOrderExt);
});