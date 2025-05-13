class Symbol:
    ...

    def send_execution_plan(self, plan: ExecutionPlan):
        """
        Translates and sends ExecutionPlan to the exchange/order gateway.
        Handles market/limit/PTA/ladder logic centrally.
        """
        side_code = {
            'buy': 'BUY',
            'sell': 'SELL'
        }

        if plan.type == 'market':
            command = [MARKETORDER, self.symbol_name, plan.size, 0, self.manager.gateway]
            self.ppro_out.send(command)

        elif plan.type == 'limit':
            command = [LIMITORDER, self.symbol_name, plan.size, plan.price, self.manager.gateway]
            self.ppro_out.send(command)

            if plan.timeout:
                threading.Timer(plan.timeout, lambda: self.cancel_or_escalate(plan)).start()

        elif plan.type == 'pta':
            # PTA: Post, wait X sec, then escalate
            self.place_passive(plan)
            if plan.timeout:
                threading.Timer(plan.timeout, lambda: self.cancel_or_escalate(plan)).start()

        elif plan.type == 'nbbo':
            # Post at best bid/ask
            price = self.get_nbbo(plan.side)
            command = [PASSIVEBUY if plan.side == 'buy' else PASSIVESELL,
                       self.symbol_name, plan.size, price, self.manager.gateway]
            self.ppro_out.send(command)

        elif plan.type == 'ladder':
            for level in plan.price_levels:  # e.g., [99.8, 99.7, 99.6]
                command = [LIMITORDER, self.symbol_name, plan.size_per_level, level, self.manager.gateway]
                self.ppro_out.send(command)

        else:
            log_print("Unknown execution plan type:", plan)



    def cancel_or_escalate(self, plan: ExecutionPlan):
        """
        Called when PTA or limit timeout expires.
        If fallback is set, execute fallback action.
        """
        self.cancel_order(plan)  # optional
        if plan.fallback == 'market':
            fallback = ExecutionPlan(
                symbol=self.symbol_name,
                side=plan.side,
                size=plan.size,
                type='market',
                tag='fallback'
            )
            self.send_execution_plan(fallback)
        elif plan.fallback == 'midpoint':
            price = self.get_midpoint()
            fallback = ExecutionPlan(
                symbol=self.symbol_name,
                side=plan.side,
                size=plan.size,
                price=price,
                type='limit',
                tag='fallback'
            )
            self.send_execution_plan(fallback)