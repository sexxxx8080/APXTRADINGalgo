import backtrader as bt

class RiskControlledStrategy(bt.Strategy):
    params = (('fast_length', 9), ('slow_length', 21), ('atr_length', 14), ('risk_per_trade', 0.01))

    def __init__(self):
        self.fast_ma = bt.ind.EMA(period=self.p.fast_length)
        self.slow_ma = bt.ind.EMA(period=self.p.slow_length)
        self.atr = bt.ind.ATR(period=self.p.atr_length)

    def next(self):
        if self.position:
            # Dynamic exit based on ATR trailing stop
            if self.position.size > 0 and self.data.close[0] < self.entryprice - self.atr[0] * 1.5:
                self.close()
            elif self.position.size < 0 and self.data.close[0] > self.entryprice + self.atr[0] * 1.5:
                self.close()

        else:
            if self.fast_ma[0] > self.slow_ma[0]:
                # Long entry
                size = self.broker.get_cash() * self.p.risk_per_trade / (self.atr[0] * 1.5)
                self.buy(size=size)
            elif self.fast_ma[0] < self.slow_ma[0]:
                # Short entry
                size = self.broker.get_cash() * self.p.risk_per_trade / (self.atr[0] * 1.5)
                self.sell(size=size)

# Backtesting setup
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(RiskControlledStrategy)
    data = bt.feeds.GenericCSVData(dataname='your_data.csv', dtformat='%Y-%m-%d', timeframe=bt.TimeFrame.Minutes)
    cerebro.adddata(data)
    cerebro.broker.set_cash(100000)
    cerebro.run()
    cerebro.plot()
