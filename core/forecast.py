import pandas as pd
import numpy as np
import tensorflow as tf

from core.errors import *


class Forecast:
    def __init__(self, series, method='rnn'):
        self.__methods = ['rnn']

        """
        if method not in self.__methods:
            raise MethodError
        """

        self.__series = series
        self.__method = method

        self.__X = None
        self.__y = None

        self.__x_data = None
        self.__x_batches = None

        self.__y_data = None
        self.__y_batches = None

        self.__X_test = None
        self.__Y_test = None

        self.__num_periods = None
        self.__horizon = None

        self.__hidden = None
        self.__inputs = None
        self.__output = None

        self.__learning_rate = None
        self.__epochs = None

        self.__loss = None
        self.__training_op = None
        self.__optimizer = None
        self.__outputs = None

        self.__y_hat = None

    def rnn(self, num_periods=5, horizon=1, hidden=100, inputs=1, output=1, learning_rate=0.001, epochs=1000):

        self.__num_periods = num_periods
        self.__horizon = horizon

        self.__hidden = hidden
        self.__inputs = inputs
        self.__output = output

        self.__learning_rate = learning_rate
        self.__epochs = epochs

    def fit(self):
        if self.__method == 'rnn':
            ts = np.array(self.__series)
            size = len(ts)

            # create batches for better gradient
            self.__x_data = ts[:size - (size % self.__num_periods)]
            self.__x_batches = self.__x_data.reshape(-1, self.__num_periods, 1)

            self.__y_data = ts[1:(size - (size % self.__num_periods)) + self.__horizon]
            self.__y_batches = self.__y_data.reshape(-1, self.__num_periods, 1)

            # create test sample
            self.__X_test, self.__Y_test = self.__test_data(ts, self.__horizon, self.__num_periods)

            # reset default graph
            tf.reset_default_graph()

            self.__X = tf.placeholder(tf.float32, [None, self.__num_periods, self.__inputs])
            self.__y = tf.placeholder(tf.float32, [None, self.__num_periods, self.__output])

            basic_cell = tf.contrib.rnn.BasicRNNCell(num_units=self.__hidden, activation=tf.nn.relu)
            rnn_output, states = tf.nn.dynamic_rnn(basic_cell, self.__X, dtype=tf.float32)

            stacked_rnn_output = tf.reshape(rnn_output, [-1, self.__hidden])
            stacked_outputs = tf.layers.dense(stacked_rnn_output, self.__output)
            self.__outputs = tf.reshape(stacked_outputs, [-1, self.__num_periods, self.__output])

            self.__loss = tf.reduce_sum(tf.square(self.__outputs - self.__y))
            self.__optimizer = tf.train.AdamOptimizer(learning_rate=self.__learning_rate)
            self.__training_op = self.__optimizer.minimize(self.__loss)
        else:
            return 'only RNN implemented'

    def predict(self):
        if self.__method == 'rnn':
            init = tf.global_variables_initializer()

            with tf.Session() as sess:
                init.run()
                for ep in range(self.__epochs):
                    sess.run(self.__training_op, feed_dict={self.__X: self.__x_batches, self.__y: self.__y_batches})
                    if ep % 100 == 0:
                        mse = self.__loss.eval(feed_dict={self.__X: self.__x_batches, self.__y: self.__y_batches})
                        print(ep, '\tMSE: ', mse)

                y_hat = sess.run(self.__outputs, feed_dict={self.__X: self.__X_test})

                self.__y_hat = [c[0] for c in y_hat[0]]

                return self.__y_hat
        else:
            return 'only RNN implemented'

    def fit_predict(self):
        self.fit()
        return self.predict()

    def __test_data(self, series, horizon, num_periods):
        test_x_setup = series[-(num_periods + horizon):]

        test_x = test_x_setup[:num_periods].reshape(-1, num_periods, 1)
        test_y = series[-num_periods:].reshape(-1, num_periods, 1)

        return test_x, test_y

    @property
    def series(self):
        return self.__series

    @property
    def num_periods(self):
        return self.__num_periods

    @num_periods.setter
    def num_periods(self, num_periods):
        self.__num_periods = num_periods

    @property
    def horizon(self):
        return self.__horizon

    @horizon.setter
    def horizon(self, horizon):
        self.__horizon = horizon

    @property
    def hidden(self):
        return self.__hidden

    @hidden.setter
    def hidden(self, hidden):
        self.__hidden = hidden

    @property
    def learning_rate(self):
        return self.__learning_rate

    @learning_rate.setter
    def learning_rate(self, learning_rate):
        self.__learning_rate = learning_rate

    @property
    def epochs(self):
        return self.__epochs

    @epochs.setter
    def epochs(self, epochs):
        self.__epochs = epochs

    @property
    def loss(self):
        return self.__loss

    @property
    def optimizer(self):
        return self.__optimizer

    @property
    def prediction(self):
        return self.__y_hat
