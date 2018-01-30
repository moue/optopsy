import optopsy as op


class SampleStrategy(op.Strategy):

    def on_init(self, **params):

        self.set_strategy_name("Sample Strategy")

        # set the backtesting params for this instance of backtest
        self.set_start_date(2016, 2, 19)
        self.set_end_date(2016, 2, 26)

        # define time events
        self.scheduler.on(self.date_rule.every(op.DayOfWeek.THURSDAY), self.filter_options)

        # add vertical put spreads for this strategy
        self.add_option_strategy(
            "VXX",
            op.OptionStrategy.VERTICAL,
            option_type=op.OptionType.PUT,
            width=self.width,
            dte=self.dte
        )

    def filter_options(self, data):
        strategy = data['VXX'].nearest('mark', 1).max('dte')
        self.buy_to_open(strategy, 10, order_type=op.OrderType.LMT, price=0.75)


if __name__ == '__main__':
    # Initiate and run a backtest of this strategy with optimization parameters
    results = op.Backtest(
        SampleStrategy,
        dte=(op.Period.SEVEN_WEEKS,),
        width=(2, 3, 4),
        roi=(1,)
    ).run()
