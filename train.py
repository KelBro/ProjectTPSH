import pandas as pd
import pyarrow.parquet as pq
from PIL import Image
from io import BytesIO
import os
import random
from ultralytics import YOLO
import torch
from torch.optim import Adam


class Train:
    def __init__(self):

        self.lls = 12

        # load the dataset and devide to 4:1
        dataPath = './data/'
        self.pathToYaml = ''
        df1 = pq.read_table(f'{dataPath}dataset1.parquet').to_pandas()
        df2 = pq.read_table(f'{dataPath}dataset2.parquet').to_pandas()
        df3 = pq.read_table(f'{dataPath}dataset3.parquet').to_pandas()
        df4 = pq.read_table(f'{dataPath}dataset4.parquet').to_pandas()
        df5 = pq.read_table(f'{dataPath}dataset5.parquet').to_pandas()

        df = pd.concat([df1,df2,df3,df4,df5]).values.tolist()
        
        for i in df:
            cef = {}
            for f in f'{i[1]}\n'.split(','):
                pr = f.split(':') 
                cef[pr[0].strip().lower()] = pr[1].strip().lower()
            i[1] = cef
        # print(str(df[0][1]), len(df), len(df[0][1]))
        self.DF = df
        self.numList = ['a dress with color', 'department', 'detail', 'fabric-elasticity', 'fit', 'hemline', 'material', 'neckline', 'pattern', 'sleeve-length', 'style', 'type', 'waistline']
        random.shuffle(df)
        df1 = df[:int(len(df)*0.7)]
        dfM = df[int(len(df)*0.7):]
        df2 = dfM[:int(len(dfM)*0.5)]
        df3 = dfM[int(len(dfM)*0.5):]

        print(str(df[0][0])[:100])
        newDf = self.saveDataset(df=self.DF)

        

        # self.convert(type = 'train', df = df1, num=self.numList[self.lls])
        # self.convert(type = 'test', df = df2, num=self.numList[self.lls])
        # self.convert(type = 'val', df = df3, num=self.numList[self.lls])
        # for i in self.numList:

        #     print(self.getClasses(df=self.DF, num=i))
    def convert(self, df:list, type:str, num:str): # part of dataframe and the type for exmp: train

        """ convert dataframe to dataframe for YOLO V8"""
        for i in range(len(df)):
            img = df[i][0]['bytes']

            img = BytesIO(img)
            img = Image.open(img)
            try:
                os.makedirs(f'./dataset{self.lls}/{type}/{df[i][1][num]}/',exist_ok=True)

                img.save(f'./dataset{self.lls}/{type}/{df[i][1][num]}/img{i}.png')
            except:''

    def saveDataset(self,df):
        """ save the dataset to usb may be """
        count = 0
        for i in df:
            # img = i[0]['bytes']
            # img = BytesIO(img)
            # img = Image.open(img)
            # img.save(f'./image/image{count}.png')
            i[0] = (f'./image/image{count}.png')
            count+=1
        df = pd.DataFrame(df,columns = ['path', 'text'])
        df.to_csv('datas.csv')
        return df

    def getClasses(self, df:list, num:str):
        """ get all class from the dataset """
        cl = []
        count = 0
        for i in df:
            try:
                if i[1][num] not in cl:
                    cl.append(i[1][num])
            except: 
                count+=1
                
        # if count!=0: print(count)
        return cl
    
    def createYAML(self, classes:list):
        """ ADD the yaml file to dataset for yolo """
        ls = self.getClasses(self.DF)
        with open(f'dataset{self.lls}/', 'w', encoding='utf-8') as file:
            file.write(f"""
        train: dataset{self.lls}/train/
        valid: dataset{self.lls}/val/
        test: dataset{self.lls}/test/

        # number of classes
        nc: {len(ls)}

        # class names
        names: {str(ls)}
        """)
    

    def train(self,num:str, data, model, epoch:int, ilr = 1e-4):
        """ train the model """

        # freezing
        for parameters in model.model.parameters():
            parameters.requires_grad = False

        layers = []
        for name, module in model.model.named_modules():
            if isinstance(module, torch.nn.Module):
                layers.append((name,model))
        
        for i, (name, layer) in enumerate(reversed(layers)):
            print(f'layer: {name}')

            for parameters in layer.parameters():
                parameters.requires_grad = True
            
            optimizer = Adam(filter(lambda p: p.requires_grad, model.model.parameters()), lr = ilr/(i+1), betas=(0.9, 0.999), eps=1e-8,weight_decay=0.0005)
            model.train(data = data, epochs = epoch, optimizer=optimizer,pretrained=False,freeze = [], verbose = True)
            model.save(f'yoloPost{i}.pt')

    def startTrain(self):
        """ start prepare for train the model """

        model = YOLO('yolov8n-cls.pt')
        trData = self.pathToYaml
        self.train(model=model, data=trData, epoch=5,ilr=1e-4)


Train()