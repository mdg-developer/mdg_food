odoo.define('pos_promotion_date.Loyalty', function(require) {
    'use strict';

const {Order, PosGlobalState} = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');

const PosLoyaltyGlobalState = (PosGlobalState) => class PosLoyaltyGlobalState extends PosGlobalState {
    _loadLoyaltyData() {
    console.log('_loadLoyaltyData')
        this.program_by_id = {};
        this.reward_by_id = {};

        for (const program of this.programs) {
        console.log('program1',program)
            this.program_by_id[program.id] = program;
            if (program.date_to) {
                program.date_to = new Date(program.date_to);
                console.log('program date to',program.date_to)
            }
            if (program.date_from) {
                program.date_from = new Date(program.date_from);
                console.log('program date from',program.date_from)
            }
            program.rules = [];
            program.rewards = [];
        }
        for (const rule of this.rules) {
            rule.valid_product_ids = new Set(rule.valid_product_ids);
            rule.program_id = this.program_by_id[rule.program_id[0]];
            rule.program_id.rules.push(rule);
        }
        for (const reward of this.rewards) {
            this.reward_by_id[reward.id] = reward
            reward.program_id = this.program_by_id[reward.program_id[0]];;
            reward.discount_line_product_id = this.db.get_product_by_id(reward.discount_line_product_id[0]);
            reward.all_discount_product_ids = new Set(reward.all_discount_product_ids);
            reward.program_id.rewards.push(reward);
        }
    }
}

Registries.Model.extend(PosGlobalState, PosLoyaltyGlobalState);


const PosLoyaltyOrderExt = (Order) => class PosLoyaltyOrderExt extends Order {
    _programIsApplicable(program) {
    console.log('program',program)
    console.log('date',new Date())
    console.log('program date to',program.date_to)
    console.log('program date from',program.date_from)
        if (program.trigger === 'auto' && !program.rules.find((rule) => rule.mode === 'auto' || this.codeActivatedProgramRules.includes(rule.id))) {
            return false;
        }
        if (program.trigger === 'with_code' && !program.rules.find((rule) => this.codeActivatedProgramRules.includes(rule.id))) {
            return false;
        }
        if (program.is_nominative && !this.get_partner()) {
            return false;
        }
        if (program.date_from && program.date_from > new Date()) {
        console.log('date_from False')
            return false;
        }
        if (program.date_to && program.date_to <= new Date) {
        console.log('date_to False')
            return false;
        }
        if (program.limit_usage && program.total_order_count >= program.max_usage) {
            return false;
        }
        return true;
    }
}



Registries.Model.extend(Order, PosLoyaltyOrderExt);
});