import numpy as np
from helpers import build_index_groups, compute_error
from ml_helpers import init_MF

def update_user_feature(
        train, item_features, lambda_user,
        nnz_items_per_user, nz_user_itemindices):
    """update user feature matrix."""
    Z_final = np.zeros((train.shape[1], item_features.shape[1]))
    for (n, d) in nz_user_itemindices:
        A = item_features[d,:].T.dot(item_features[d,:]) + lambda_user*np.identity(item_features.shape[1])
        b  = np.squeeze(np.asarray(item_features[d,:].T * train[d,n]))
        Z_final[n,:] = np.linalg.solve(A, b)
    return Z_final

def update_item_feature(
        train, user_features, lambda_item,
        nnz_users_per_item, nz_item_userindices):
    """update item feature matrix."""
    W_final = np.zeros((train.shape[0], user_features.shape[1]))
    for (d, n) in nz_item_userindices:
        A = user_features[n,:].T.dot(user_features[n,:]) + lambda_item*np.identity(user_features.shape[1])
        b  = np.squeeze(np.asarray(user_features[n,:].T * train[d,n].T))
        W_final[d,:] = np.linalg.solve(A, b)
    return W_final

def ALS(train, test, n_f, l_u, l_i):
    """Alternating Least Squares (ALS) algorithm."""
    # define parameters
    num_features = n_f   # K in the lecture notes
    lambda_user = l_u
    lambda_item = l_i
    stop_criterion = 1e-4

    # set seed
    np.random.seed(988)

    # init ALS
    user_features, item_features = init_MF(train, num_features)

    # find the non-zero ratings indices
    nz_train, nz_item_userindices, nz_user_itemindices = build_index_groups(train)
    nz_row, nz_col = test.nonzero()
    nz_test = list(zip(nz_row, nz_col))

    rmse = compute_error(train, user_features, item_features, nz_train)
    delta_rmse = np.inf
    it = 0
    while np.abs(delta_rmse - rmse) > stop_criterion:
        user_features = update_user_feature(train, item_features, lambda_user, train.nnz, nz_user_itemindices)
        item_features = update_item_feature(train, user_features, lambda_item, train.nnz, nz_item_userindices)
        delta_rmse = rmse
        rmse = compute_error(train, user_features, item_features, nz_train)
        it += 1
        print("iter: {}, RMSE on training set: {}.".format(it, rmse))

    rmse_test = compute_error(test, user_features, item_features, nz_test)
    print("RMSE on testing set: {}.".format(rmse_test))

    return item_features.dot(user_features.T)