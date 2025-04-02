from ultralytics import YOLO





class Classification():
    def __init__(self):
        self.mdp = 'best.pt'

        Classification.DetectModel = YOLO('./help/best.pt')
        Classification.fabricElasticityModel = YOLO('./help/fabric-elasticity.pt')
        Classification.fitClasses = YOLO('./help/fit.pt')
        Classification.ColorModel = YOLO('./help/color.pt')
        Classification.DetailModel = YOLO('./help/Detail.pt')
        Classification.HemlineModel = YOLO('./help/hemline.pt')
        Classification.MaterialModel = YOLO('./help/material.pt')
        Classification.NecklineModel = YOLO('./help/neckline.pt')
        Classification.PatternModel = YOLO('./help/pattern.pt')
        Classification.StyleModel = YOLO('./help/style.pt')
        Classification.typeModel = YOLO('./help/type.pt')
        Classification.WaistLineModel = YOLO('./help/waistline.pt')
        print(''.join(['=' for _ in range(52)])+'\n==- System message -====- thank that you chose us -==\n'+''.join(['=' for _ in range(52)]))



        # a= Classification.GetMark(imgPath=input('[exit if you want to exit]  IMG path: '))
        # print(a)
            
        # while 'y' in input('continue? [y/n] ').lower():
        #     self.useModel(modelPath=self.mdp if 'y' in input(f'use {self.mdp} model? [y/n]' ).lower() else self.saveChose(),
        #                   imgPath=input('please print path to the photo and the name of the photo:  ')
        #                   )
            

    def GetMark(imgPath):
        a = Classification.DetectModel(imgPath)
        asw = set([a[0].names[int(cls)] for cls in a[0].boxes.cls])
        if 'clothing' not in str(asw):
            return {'department':'it not a dress'}
        try:
            color = Classification.ColorModel.predict(imgPath)[0]
        except: color = None
        # department = Model.predict(imgPath)[0] # always is dress
        try:
            detail = Classification.DetailModel.predict(imgPath)[0]
        except: detail = None
        try:
            fabricE = Classification.fabricElasticityModel.predict(imgPath)[0]
        except: fabricE = None
        try:
            fit = Classification.fitClasses.predict(imgPath)[0]
        except: fit =None
        try:
            hemline = Classification.HemlineModel.predict(imgPath)[0]
        except: hemline = None
        try:
            material = Classification.MaterialModel.predict(imgPath)[0]
        except: material =None
        try:
            neckline = Classification.NecklineModel.predict(imgPath)[0]
        except: neckline = None
        try:
            pattern = Classification.PatternModel.predict(imgPath)[0]
        except: pattern = None
        try:
            style = Classification.StyleModel.predict(imgPath)[0]
        except: style = None
        try:
            typet = Classification.typeModel.predict(imgPath)[0]
        except:
            typet =None
        try:
            waistline = Classification.WaistLineModel.predict(imgPath)[0]
        except: 
            waistline = None


        return {
            'a dress with color':Classification.ColorModel.names[color.probs.top1] if color!=None else 'Not Found',  
            'detail':Classification.DetailModel.names[detail.probs.top1] if detail!=None else 'Not Found', 
            'fabric-elasticity':Classification.fabricElasticityModel.names[fabricE.probs.top1] if fabricE!=None else 'Not Found', 
            'fit':Classification.fitClasses.names[fit.probs.top1] if fit!=None else 'Not Found', 'hemline':Classification.HemlineModel.names[hemline.probs.top1] if hemline!=None else 'Not Found', 
            'material':Classification.MaterialModel.names[material.probs.top1] if material!=None else 'Not Found', 
            'neckline':Classification.NecklineModel.names[neckline.probs.top1] if neckline!=None else 'Not Found', 
            'pattern':Classification.PatternModel.names[pattern.probs.top1] if pattern!=None else 'Not Found', 
            'style':Classification.StyleModel.names[style.probs.top1] if style!=None else 'Not Found', 'type':Classification.typeModel.names[typet.probs.top1] if typet!=None else 'Not Found', 
            'waistline':Classification.WaistLineModel.names[waistline.probs.top1] if waistline!=None else 'Not Found'
            }

    def saveChose(self):
        self.mdp = input('please print path to the model: ')
        self.mdp

    def IsCloth(self, imgPath:str):
        """ verifing the dress """

        a = Classification.DetectModel(imgPath)
        asw = set([a[0].names[int(cls)] for cls in a[0].boxes.cls])
        return True if 'clothing' in str(asw) else False
    def useModel(self, modelPath:str, imgPath:str):
        """use the created model """
        model = YOLO(modelPath)

        result = model.predict(imgPath)[0]
        t1 = result.probs.top1



        print(''.join(['-' for _ in range(100)])+'\n')
        print(result.probs.top5,'\n',f'1. {model.names[result.probs.top1]} : {result.probs.top1conf}\n')
        return model.names[result.probs.top1]

Classification()
