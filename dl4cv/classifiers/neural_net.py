import numpy as np
import time


def print_step_summary_and_update_best_values(epoch, train_loss,
                                              train_accuracy, test_loss, test_accuracy, duration):
    # print table header again after every 3000th step
    if epoch % 100 == 0 and epoch > 0:
        print('Epoch\tTrain Loss\tTrain accuracy\t\tTest Loss\tTest accuracy\tDuration')
    train_string = '{0:.5f}\t\t{1:.2f}%\t\t\t'.format(train_loss, train_accuracy * 100)
    test_string = '{0:.5f}\t\t{1:.2f}%\t\t'.format(test_loss, test_accuracy * 100)

    print('{0}\t'.format(epoch) + train_string + test_string + '{0:.3f}'.format(duration))


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network. The net has an input dimension of
    N, a hidden layer dimension of H, and performs classification over C classes.
    We train the network with a softmax loss function and L2 regularization on the
    weight matrices. The network uses a ReLU nonlinearity after the first fully
    connected layer.

    In other words, the network has the following architecture:

    input - fully connected layer - ReLU - fully connected layer - softmax

    The outputs of the second fully-connected layer are the scores for each class.
    """

    def __init__(self, input_size, hidden_size, output_size, std=1e-4):
        """
        Initialize the model. Weights are initialized to small random values and
        biases are initialized to zero. Weights and biases are stored in the
        variable self.params, which is a dictionary with the following keys:

        W1: First layer weights; has shape (D, H)
        b1: First layer biases; has shape (H,)
        W2: Second layer weights; has shape (H, C)
        b2: Second layer biases; has shape (C,)

        Inputs:
        - input_size: The dimension D of the input data.
        - hidden_size: The number of neurons H in the hidden layer.
        - output_size: The number of classes C.
        """
        self.params = {}
        self.params['W1'] = std * np.random.randn(input_size, hidden_size)
        self.params['b1'] = np.zeros(hidden_size)
        self.params['W2'] = std * np.random.randn(hidden_size, output_size)
        self.params['b2'] = np.zeros(output_size)

    def loss(self, X, y=None, reg=0.0, dropout=(0.0, False)):
        """
        Compute the loss and gradients for a two layer fully connected neural
        network.

        Inputs:
        - X: Input data of shape (N, D). Each X[i] is a training sample.
        - y: Vector of training labels. y[i] is the label for X[i], and each y[i] is
          an integer in the range 0 <= y[i] < C. This parameter is optional; if it
          is not passed then we only return scores, and if it is passed then we
          instead return the loss and gradients.
        - reg: Regularization strength.

        Returns:
        If y is None, return a matrix scores of shape (N, C) where scores[i, c] is
        the score for class c on input X[i].

        If y is not None, instead return a tuple of:
        - loss: Loss (data loss and regularization loss) for this batch of training
          samples.
        - grads: Dictionary mapping parameter names to gradients of those parameters
          with respect to the loss function; has the same keys as self.params.
        """
        # Unpack variables from the params dictionary
        dropout_percent, do_dropout = dropout
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        N, D = X.shape
        C = b2.shape[0]

        # Compute the forward pass
        scores = None
        #############################################################################
        # TODO: Perform the forward pass, computing the class scores for the input. #
        # Store the result in the scores variable, which should be an array of      #
        # shape (N, C).                                                             #
        #############################################################################

        # compute activations for layer 1 using Relu
        l1_input = np.dot(X, W1) + b1
        l1_activation = l1_input * (l1_input > 0)

        if do_dropout and dropout_percent > 0.0:
            dropout_layer = np.random.binomial([np.ones((N, W1.shape[1]))], 1 - dropout_percent)[0] * (1.0 / (1 - dropout_percent))
            l1_activation *= dropout_layer

        # compute activations for layer 2 using softmax
        scores = np.dot(l1_activation, W2) + b2

        #############################################################################
        #                              END OF YOUR CODE                             #
        #############################################################################

        # If the targets are not given then jump out, we're done
        if y is None:
            return scores

        # Compute the loss
        loss = None
        #############################################################################
        # TODO: Finish the forward pass, and compute the loss. This should include  #
        # both the data loss and L2 regularization for W1 and W2. Store the result  #
        # in the variable loss, which should be a scalar. Use the Softmax           #
        # classifier loss. So that your results match ours, multiply the            #
        # regularization loss by 0.5                                                #
        #############################################################################

        # compute softmax
        # take care of potential numerical issues
        scores -= np.max(scores, axis=1, keepdims=True)

        scores = np.exp(scores) / np.sum(np.exp(scores), axis=1, keepdims=True)

        losses = - np.log(scores[range(N), y])
        loss = np.sum(losses) / N

        # add regularization for loss
        loss += 0.5 * reg * (
            np.sum(W1 ** 2) +
            np.sum(W2 ** 2)
        )

        #############################################################################
        #                              END OF YOUR CODE                             #
        #############################################################################

        # Backward pass: compute gradients
        grads = {}
        #############################################################################
        # TODO: Compute the backward pass, computing the derivatives of the weights #
        # and biases. Store the results in the grads dictionary. For example,       #
        # grads['W1'] should store the gradient on W1, and be a matrix of same size #
        #############################################################################

        # convert labels to one-hot
        y_one_hot = np.zeros((N, C))
        y_one_hot[np.arange(N), y] = 1

        # gradients for weights of second layer (L = Loss, h_j = activations of L1, y_1 = scores, t_i = true label
        # dL
        # --        = h_j * t_s
        # dW2_ij
        # and t_s = (y_i - t_i)
        true_scores = (scores - y_one_hot) / N
        dW2 = np.dot(l1_activation.T, true_scores)

        db2 = np.sum(true_scores, axis=0, keepdims=True)

        # dW1
        dW1 = np.dot(true_scores, W2.T)
        # derivative of relu is
        # dRelu(0) = 0
        # dRelu(>0) = 1
        dW1[l1_activation <= 0] = 0
        db1 = np.sum(dW1, axis=0, keepdims=True)

        dW1 = np.dot(X.T, dW1)

        dW1 += reg * W1
        dW2 += reg * W2

        grads['W1'] = dW1
        grads['W2'] = dW2
        grads['b1'] = db1
        grads['b2'] = db2

        #############################################################################
        #                              END OF YOUR CODE                             #
        #############################################################################

        return loss, grads

    def train(self, X, y, X_val, y_val,
              learning_rate=1e-3, learning_rate_decay=0.95,
              reg=1e-5, num_iters=100,
              batch_size=200,
              dropout=(0.5, False),
              random_flip=None,
              verbose=False):
        """
        Train this neural network using stochastic gradient descent.

        Inputs:
        - X: A numpy array of shape (N, D) giving training data.
        - y: A numpy array f shape (N,) giving training labels; y[i] = c means that
          X[i] has label c, where 0 <= c < C.
        - X_val: A numpy array of shape (N_val, D) giving validation data.
        - y_val: A numpy array of shape (N_val,) giving validation labels.
        - learning_rate: Scalar giving learning rate for optimization.
        - learning_rate_decay: Scalar giving factor used to decay the learning rate
          after each epoch.
        - reg: Scalar giving regularization strength.
        - num_iters: Number of steps to take when optimizing.
        - batch_size: Number of training examples to use per step.
        - verbose: boolean; if true print progress during optimization.
        """
        num_train = X.shape[0]
        iterations_per_epoch = max(num_train // batch_size, 1)

        # Use SGD to optimize the parameters in self.model
        loss_history = []
        train_acc_history = []
        val_acc_history = []
        val_loss_history = []

        # this is only theoretical since we sample with replacing
        best_validation_accuracy = -1
        best_model = {}
        early_stopping_counter = 10

        print('Epoch\tTrain Loss\tTrain accuracy\t\tTest Loss\tTest accuracy\tDuration')
        print('=====================================================================================================')
        start_time = time.time()
        average_train_loss = 0
        for it in range(num_iters):
            X_batch = None
            y_batch = None

            #########################################################################
            # TODO: Create a random minibatch of training data and labels, storing  #
            # them in X_batch and y_batch respectively.                             #
            #########################################################################

            batch_indices = np.random.choice(num_train, batch_size)
            X_batch = X[batch_indices]
            y_batch = y[batch_indices]

            if random_flip is not None:
                # how many images should we flip?
                num_images_to_flip = max(1, round(batch_size * random_flip))
                images_to_flip_indices = np.random.choice(batch_size, num_images_to_flip, replace=False)

                X_batch[images_to_flip_indices] = np.fliplr(X_batch[images_to_flip_indices])

            #########################################################################
            #                             END OF YOUR CODE                          #
            #########################################################################

            # Compute loss and gradients using the current minibatch
            loss, grads = self.loss(X_batch, y=y_batch, reg=reg, dropout=dropout)
            loss_history.append(loss)
            average_train_loss += loss

            #########################################################################
            # TODO: Use the gradients in the grads dictionary to update the         #
            # parameters of the network (stored in the dictionary self.params)      #
            # using stochastic gradient descent. You'll need to use the gradients   #
            # stored in the grads dictionary defined above.                         #
            #########################################################################

            self.params['W1'] -= learning_rate * grads['W1']
            self.params['W2'] -= learning_rate * grads['W2']
            self.params['b1'] -= learning_rate * grads['b1'][0]
            self.params['b2'] -= learning_rate * grads['b2'][0]

            #########################################################################
            #                             END OF YOUR CODE                          #
            #########################################################################

            if verbose and it % 100 == 0:
                print('iteration %d / %d: loss %f' % (it, num_iters, loss))

            # Every epoch, check train and val accuracy and decay learning rate.
            if it % iterations_per_epoch == 0:
                duration = time.time() - start_time
                start_time = time.time()
                epoch = it / iterations_per_epoch

                # Check accuracy
                train_acc = (self.predict(X_batch) == y_batch).mean()
                val_acc = (self.predict(X_val) == y_val).mean()
                train_acc_history.append(train_acc)
                val_acc_history.append(val_acc)

                # get valid loss
                val_loss = self.loss(X_val, y_val, reg=reg)[0]
                val_loss_history.append(val_loss)

                # don't take the average in the first step
                if epoch > 0:
                    average_train_loss /= iterations_per_epoch

                print_step_summary_and_update_best_values(epoch, average_train_loss, train_acc,
                                                          val_loss, val_acc, duration)

                # reset for the next epoch
                average_train_loss = 0

                # early stopping if no improvement of val_acc during the last 5 epochs
                # https://link.springer.com/chapter/10.1007/978-3-642-35289-8_5
                if val_acc > best_validation_accuracy:
                    best_validation_accuracy = val_acc
                    best_model = {
                        'W1': self.params['W1'].copy(),
                        'W2': self.params['W2'].copy(),
                        'b1': self.params['b1'].copy(),
                        'b2': self.params['b2'].copy(),
                    }
                    early_stopping_counter = 10

                else:
                    early_stopping_counter -= 1

                    # if early_stopping_counter is 0 restore best weights and stop training
                    if early_stopping_counter <= 0:
                        print('> Early Stopping after 10 epochs of no improvements.')
                        print('> Restoring params of best model with validation accuracy of: '
                              , best_validation_accuracy)
                        self.params = best_model
                        break

                # Decay learning rate
                learning_rate *= learning_rate_decay
        print('=====================================================================================================')

        return {
            'loss_history': loss_history,
            'train_acc_history': train_acc_history,
            'val_acc_history': val_acc_history,
            'val_loss_history': val_loss_history,
        }

    def predict(self, X):
        """
        Use the trained weights of this two-layer network to predict labels for
        data points. For each data point we predict scores for each of the C
        classes, and assign each data point to the class with the highest score.

        Inputs:
        - X: A numpy array of shape (N, D) giving N D-dimensional data points to
          classify.

        Returns:
        - y_pred: A numpy array of shape (N,) giving predicted labels for each of
          the elements of X. For all i, y_pred[i] = c means that X[i] is predicted
          to have class c, where 0 <= c < C.
        """
        y_pred = None

        ###########################################################################
        # TODO: Implement this function; it should be VERY simple!                #
        ###########################################################################

        # compute activations for layer 1 using Relu
        l1_input = np.dot(X, self.params['W1']) + self.params['b1']
        l1_activation = l1_input * (l1_input > 0)

        # compute activations for layer 2 using softmax
        scores = np.dot(l1_activation, self.params['W2']) + self.params['b2']
        # compute softmax
        # take care of potential numerical issues
        scores -= np.max(scores, axis=1, keepdims=True)
        y_pred = np.argmax(np.exp(scores) / np.sum(np.exp(scores), axis=1, keepdims=True), axis=1)

        ###########################################################################
        #                              END OF YOUR CODE                           #
        ###########################################################################

        return y_pred
