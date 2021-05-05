import pandas as pd
import numpy as np
import sklearn.preprocessing
import imblearn

from dsutils import DataDir
from typing import Tuple


class DiabetesData(DataDir):

    def __init__(self, csvfile: str, classcol: str = 'class') -> None:
        super().__init__()
        csvfile = self.datafilename(csvfile)
        self._fulldata = pd.read_csv(csvfile)

        if classcol not in self._fulldata.columns:
            raise ValueError(f"'{classcol}' must exist in '{csvfile}'")

        self._classcol = classcol

    @property
    def datafull(self) -> pd.DataFrame:
        return self._fulldata

    @property
    def data(self) -> pd.DataFrame:
        return self.datafull.drop(columns=[self._classcol])

    @property
    def dataclass(self) -> pd.DataFrame:
        return self.datafull[[self._classcol]]

    @property
    def datanum(self) -> pd.DataFrame:
        normalizer = sklearn.preprocessing.MinMaxScaler()
        data = self.data.select_dtypes(include=np.number)
        normal = normalizer.fit_transform(data)
        return pd.DataFrame(normal, columns=data.columns)

    @property
    def datacat(self) -> pd.DataFrame:
        data = self.data.select_dtypes(include=object)
        data = pd.get_dummies(data) if data.size > 0 else data
        return data

    @property
    def datanormal(self) -> pd.DataFrame:
        return self.datanum.join(self.datacat)

    @property
    def datafullbalanced(self) -> pd.DataFrame:
        oversample = imblearn.over_sampling.SMOTE()
        x, y = oversample.fit_resample(self.datanormal, self.dataclass)
        return x.join(y)

    @property
    def datasplit(self) -> Tuple[pd.DataFrame, pd.DataFrame,
                                 pd.DataFrame, pd.DataFrame]:
        balanced = self.datafullbalanced
        x = balanced.drop(columns=[self._classcol])
        y = balanced[[self._classcol]]
        return sklearn.model_selection.train_test_split(x, y, test_size=0.3)


class Diabetes(DiabetesData):

    def __init__(self):
        super().__init__('diabetes.csv')
        self.xtrain, self.xtest, self.ytrain, self.ytest = self.datasplit
        print(self.xtrain.head())
        print(self.ytrain.shape)
        print(type(self.datafull['class']))

    @property
    def model(self):
        model = sklearn.ensemble.RandomForestClassifier()
        return model.fit(self.xtrain, self.ytrain)





