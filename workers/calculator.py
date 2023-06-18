from utils import *
from containers.measurement import Measurement
from containers.rmse import RMSE

class CalculatorWorker(QObject):
    emit_I1I3 = Signal(pd.DataFrame)
    emit_RMSE = Signal(RMSE)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.measurements:list[Measurement] = []

    def load(self, measurements:list):
        self.measurements = measurements
        regression_data = self.__prepare_regression_data()
        model_data = self.__prepare_models(regdata=regression_data)
        R2val, RMSEval = self.__define_best(model_data=model_data)
        model1, model2 = model_data.loc[RMSEval,['model1','model2']]
        cac_data = self.__calculate_cac(model1, model2)
        rmse_data = RMSE(regression_data, RMSEval, cac_data)
        self.emit_RMSE.emit(rmse_data)

    def __prepare_regression_data(self)->pd.DataFrame:
        concentrations: list[float] = [log10(measurement.concentration) for measurement in self.measurements if measurement.enabled]
        relatives:list[float] = [float(measurement.peaks["Peak 1"]/measurement.peaks["Peak 2"]) for measurement in self.measurements if measurement.enabled]
        
        d = {"concentration(log)" : concentrations, "I1/I3" : relatives}
        I1I3 = pd.DataFrame(data=d)
        I1I3["I1"] = [float(measurement.peaks["Peak 1"]) for measurement in self.measurements if measurement.enabled]
        I1I3["I3"] = [float(measurement.peaks["Peak 2"]) for measurement in self.measurements if measurement.enabled]
        I1I3["concentration"] = [measurement.concentration for measurement in self.measurements if measurement.enabled]
        I1I3.set_index("concentration(log)", inplace=True)
        self.emit_I1I3.emit(I1I3)
        
        regression_data = pd.DataFrame({'Y': relatives,'X': concentrations})
        regression_data.sort_values('X', inplace=True)
        return regression_data.T
    
    def __prepare_models(self, regdata:pd.DataFrame)->pd.DataFrame:
        X = regdata.loc['X'].to_numpy().reshape((-1, 1)) # the reshape is required
        Y = regdata.loc['Y'].to_numpy()
        model_data = {}
        for i in range(2,len(X)-2): # covers all possible models
            x1,x2 = X[:i],X[i:]
            y1,y2 = Y[:i],Y[i:]
            model1, model2 = LinearRegression().fit(x1,y1), LinearRegression().fit(x2,y2)
            prediction1, prediction2 = model1.predict(x1), model2.predict(x2)
            rmse1, rmse2 = self.__calculate_rmse(y1,prediction1), self.__calculate_rmse(y2,prediction2)
            rsq1, rsq2 = model1.score(x1,y1), model2.score(x2,y2) # coeficient of determination R^2
            model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'model1':model1, 'model2':model2}
            # model_data[i] = {'RMSE':rmse1+rmse2, 'R2':rsq1+rsq2, 'models':(model1, model2)} # Potentialy easier to manage
        model_data = pd.DataFrame(model_data).T # swapping the usual conversion because of needing columns to be numeric
        model_data = model_data.astype({'R2': 'Float64', 'RMSE': 'Float64'})
        return model_data

    def __define_best(self, model_data:pd.DataFrame)->tuple:
        '''Finds the best models and returns the row id as a tuple\n
        Made this way to be easily able to both find the models in a dataframe and split the point'''
        best_R2 = model_data['R2'].idxmax()
        best_RMSE = model_data['RMSE'].idxmin()
        return best_R2,best_RMSE
        
    def __calculate_rmse(self, y, ypredict):
        mse = np.square(np.subtract(y,ypredict))
        rmse = np.sqrt(np.sum(mse)/len(y))
        return rmse
    
    def __calculate_cac(self, model1:LinearRegression, model2:LinearRegression)->dict:
        cac_data = {}
        b1, b2 = model1.intercept_, model2.intercept_
        a1, a2 = model1.coef_, model2.coef_
    
        cac_data["b1"] = b1
        cac_data["b2"] = b2
        cac_data["a1"] = a1
        cac_data["a2"] = a2
        
        cac_x = (b2-b1)/(a1-a2)
        cac_y = a1*cac_x + b1
        
        cac_data["cac_x"] = cac_x
        cac_data["cac_y"] = cac_y
    
        return cac_data