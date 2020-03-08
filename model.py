def fit_model (y, X=None, test_size=12, log_model=True):
    
    try:
        if not X.empty:
            exog = True
    except:
        exog = False
        
    import numpy as np
    if log_model:
        y = y.apply(np.log)
        if exog:
            X = X.apply(np.log)
    
    train_size = int(len(df)) - test_size
    y_train, y_test = y.iloc[:-test_size], y.iloc[-test_size:]
    
    if exog:
        
        X_train, X_test = X.iloc[:-test_size], X.iloc[-test_size:]
        
        from pmdarima.arima import auto_arima
        step_wise = auto_arima(y_train, exogenous= X_train, 
                               trace=True, error_action='ignore', suppress_warnings=True,
                               start_p=0, max_p=3,
                               start_d=0, max_d=1,
                               start_q=0, max_q=3)
        
        import statsmodels.api as sm
        model = sm.tsa.statespace.SARIMAX(y_train, X_train, 
                                          order=step_wise.order, 
                                          enforce_stationarity=False, 
                                          enforce_invertibility=False).fit()
        
        pred = model.predict(start=train_size, end=train_size+test_size-1, exog=X_test)
        
    else:
        
        from pmdarima.arima import auto_arima
        step_wise = auto_arima(y_train, 
                               trace=True, error_action='ignore', suppress_warnings=True,
                               start_p=0, max_p=3,
                               start_d=0, max_d=1,
                               start_q=0, max_q=3)
        
        import statsmodels.api as sm
        model = sm.tsa.statespace.SARIMAX(y_train, 
                                          order=step_wise.order, 
                                          enforce_stationarity=False, 
                                          enforce_invertibility=False).fit()
        
        pred = model.predict(start=train_size, end=train_size+test_size-1)
    
    pred = pd.DataFrame(pred).rename(columns={0: 'predicted'}).reset_index(drop=True)
    pred.index = y_test.index
    
    if log_model:
        pred = pred.apply(np.exp)
        y_test = y_test.apply(np.exp)
        y = y.apply(np.exp)
    
    y.join(pred).plot(figsize=(20,8))
    
    from statsmodels.tools.eval_measures import rmse
    print(f'Order: {step_wise.order}')
    print(f'Error (RMSE): {rmse(pred, y_test)}')
    
    return model
    

df = dataset.dropna()

# adding dummies
df['d_2017'] = np.exp(0)
df.loc[df.index >= '2017-01-01', 'd_2017'] = np.exp(1)

renda = fit_model(df[['renda']], test_size=4)
varejo = fit_model(df[['varejo']], df[['renda', 'd_2017']])
