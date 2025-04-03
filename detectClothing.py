from ultralytics import YOLO
import os
import threading
import cv2


class Classification:
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

        print(''.join(['=' for _ in range(53)]) + '\n==- System message -====- thank that you chose us -==\n' + ''.join(
            ['=' for _ in range(53)]))

        # a= Classification.GetMark(imgPath=input('[exit if you want to exit]  IMG path: '))
        # print(a)

        # while 'y' in input('continue? [y/n] ').lower():
        #     self.useModel(modelPath=self.mdp if 'y' in input(f'use {self.mdp} model? [y/n]' ).lower() else self.saveChose(),
        #                   imgPath=input('please print path to the photo and the name of the photo:  ')
        #                   )

    def GetMark(imgPath):
        global color, detail, fabricE, fit, hemline, material, neckline, pattern, style, typet, waistline

        def fcolor():
            global color
            try:
                color = Classification.ColorModel.predict(imgPath)[0]
            except Exception as e:
                print(e)
                color = None

        def fdetail():
            global detail
            try:
                detail = Classification.DetailModel.predict(imgPath)[0]
            except Exception as e:
                print(e)
                detail = None

        def ffabric():
            global fabricE
            try:
                fabricE = Classification.fabricElasticityModel.predict(imgPath)[0]
            except:
                fabricE = None

        def ffit():
            global fit
            try:
                fit = Classification.fitClasses.predict(imgPath)[0]
            except:
                fit = None

        def fhemline():
            global hemline
            try:
                hemline = Classification.HemlineModel.predict(imgPath)[0]
            except:
                hemline = None

        def fmaterial():
            global material
            try:
                material = Classification.MaterialModel.predict(imgPath)[0]
            except:
                material = None

        def fneckline():
            global neckline
            try:
                neckline = Classification.NecklineModel.predict(imgPath)[0]
            except:
                neckline = None

        def fpattern():
            global pattern
            try:
                pattern = Classification.PatternModel.predict(imgPath)[0]
            except:
                pattern = None

        def fstyle():
            global style
            try:
                style = Classification.StyleModel.predict(imgPath)[0]
            except:
                style = None

        def ftypet():
            global typet
            try:
                typet = Classification.typeModel.predict(imgPath)[0]
            except:
                typet = None
            #os._exit(0)

        def fwaistline():
            global waistline
            try:
                waistline = Classification.WaistLineModel.predict(imgPath)[0]
            except:
                waistline = None

        # image = cv2.imread('./1img.jpg')
        # a = model(image)
        # targ = 'clothing'
        # print(a)
        # # for res in a:
        # #     boxes = res.boxes.xyxy
        # #     for box in boxes:
        # #         x1, y1, x2, y2 = map(int, box)

        # #         img = image[y1:y2, x1:x2]
        # #         cv2.imwrite("./1im.jpg", img)

        # for box, cls in zip(*[a[0].boxes.xyxy.cpu().numpy(), a[0].boxes.cls.cpu().numpy()]):
        #     if model.names[int(cls)] == targ:
        #         x1,y1,x2,y2 = map(int,box)

        #         img = image[y1:y2, x1:x2]
        #         cv2.imwrite("./1im.jpg", img)

        imgPath = cv2.imread(imgPath)
        a = Classification.DetectModel(imgPath)

        y1 = 10000000000000
        y2 = 0
        x1 = 10000000000000
        x2 = 0
        targ = 'clothing'
        stl = False

        confs = a[0].boxes.conf.cpu().numpy()

        for box, cls, conf in zip(*[a[0].boxes.xyxy.cpu().numpy(), a[0].boxes.cls.cpu().numpy(), confs]):
            print(conf)
            if Classification.DetectModel.names[int(cls)] == targ and conf > 0.7:
                stl = True
                Nx1, Ny1, Nx2, Ny2 = map(int, box)
                if Nx1 < x1:
                    x1 = Nx1
                if Ny1 < y1:
                    y1 = Ny1
                if Nx2 > x2:
                    x2 = Nx2
                if Ny2 > y2:
                    y2 = Ny2
                print(x1, y1, x2, y2)
                imgPath = imgPath[y1:y2, x1:x2]
                cv2.imwrite("./1im.jpg", imgPath)
        imgPath = "./1im.jpg"

        if not stl:
            return {'department': 'it not a dress'}

        fs = [ftypet, fwaistline, fstyle, fpattern, fneckline, fmaterial, fhemline, ffit, ffabric, fdetail, fcolor]

        for i in range(len(fs)):
            exec(f'p{i} = threading.Thread(target = fs[{i}]())')
        for i in range(len(fs)):
            exec(f'p{i}.start()')
        for i in range(len(fs)):
            exec(f'p{i}.join()')
        print(conf)

        a = {'department': 'dress',
             'a dress with color': Classification.ColorModel.names[color.probs.top1]
             if color is not None else 'Not Found',

             'detail': Classification.DetailModel.names[detail.probs.top1]
             if detail is not None else 'Not Found',

             'fabric-elasticity': Classification.fabricElasticityModel.names[fabricE.probs.top1]
             if fabricE is not None else 'Not Found',

             'fit': Classification.fitClasses.names[fit.probs.top1]
             if fit is not None else 'Not Found',

             'hemline': Classification.HemlineModel.names[hemline.probs.top1]
             if hemline is not None else 'Not Found',

             'material': Classification.MaterialModel.names[material.probs.top1]
             if material is not None else 'Not Found',

             'neckline': Classification.NecklineModel.names[neckline.probs.top1]
             if neckline is not None else 'Not Found',

             'pattern': Classification.PatternModel.names[pattern.probs.top1]
             if pattern is not None else 'Not Found',

             'style': Classification.StyleModel.names[style.probs.top1]
             if style is not None else 'Not Found',

             'type': Classification.typeModel.names[typet.probs.top1]
             if typet is not None else 'Not Found',

             'waistline': Classification.WaistLineModel.names[waistline.probs.top1]
             if waistline is not None else 'Not Found'
             }
        print(str(a))
        return a

    def GetMarkNotParallel(imgPath):
        a = Classification.DetectModel(imgPath)
        asw = set([a[0].names[int(cls)] for cls in a[0].boxes.cls])
        if 'clothing' not in str(asw):
            return {'department': 'it not a dress'}

        try:
            color = Classification.ColorModel.predict(imgPath)[0]
        except:
            color = None

        # department = Model.predict(imgPath)[0] # always is dress
        try:
            detail = Classification.DetailModel.predict(imgPath)[0]
        except:
            detail = None

        try:
            fabricE = Classification.fabricElasticityModel.predict(imgPath)[0]
        except:
            fabricE = None

        try:
            fit = Classification.fitClasses.predict(imgPath)[0]
        except:
            fit = None

        try:
            hemline = Classification.HemlineModel.predict(imgPath)[0]
        except:
            hemline = None

        try:
            material = Classification.MaterialModel.predict(imgPath)[0]
        except:
            material = None

        try:
            neckline = Classification.NecklineModel.predict(imgPath)[0]
        except:
            neckline = None

        try:
            pattern = Classification.PatternModel.predict(imgPath)[0]
        except:
            pattern = None

        try:
            style = Classification.StyleModel.predict(imgPath)[0]
        except:
            style = None

        try:
            typet = Classification.typeModel.predict(imgPath)[0]
        except:
            typet = None

        try:
            waistline = Classification.WaistLineModel.predict(imgPath)[0]
        except:
            waistline = None

        return {
            'a dress with color': Classification.ColorModel.names[color.probs.top1]
            if color is not None else 'Not Found',

            'detail': Classification.DetailModel.names[detail.probs.top1]
            if detail is not None else 'Not Found',

            'fabric-elasticity': Classification.fabricElasticityModel.names[fabricE.probs.top1]
            if fabricE is not None else 'Not Found',

            'fit': Classification.fitClasses.names[fit.probs.top1]
            if fit is not None else 'Not Found',

            'hemline': Classification.HemlineModel.names[hemline.probs.top1]
            if hemline is not None else 'Not Found',

            'material': Classification.MaterialModel.names[material.probs.top1]
            if material is not None else 'Not Found',
            'neckline': Classification.NecklineModel.names[neckline.probs.top1]
            if neckline is not None else 'Not Found',

            'pattern': Classification.PatternModel.names[pattern.probs.top1]
            if pattern is not None else 'Not Found',

            'style': Classification.StyleModel.names[style.probs.top1]
            if style is not None else 'Not Found',

            'type': Classification.typeModel.names[typet.probs.top1]
            if typet is not None else 'Not Found',

            'waistline': Classification.WaistLineModel.names[waistline.probs.top1]
            if waistline is not None else 'Not Found'
        }

    def saveChose(self):
        self.mdp = input('please print path to the model: ')
        self.mdp

    def IsCloth(self, imgPath: str):
        """ verifing the dress """

        a = Classification.DetectModel(imgPath)
        asw = set([a[0].names[int(cls)] for cls in a[0].boxes.cls])
        return True if 'clothing' in str(asw) else False

    def useModel(self, modelPath: str, imgPath: str):
        """use the created model """
        model = YOLO(modelPath)

        result = model.predict(imgPath)[0]
        t1 = result.probs.top1

        print(''.join(['-' for _ in range(100)]) + '\n')
        print(result.probs.top5, '\n', f'1. {model.names[result.probs.top1]} : {result.probs.top1conf}\n')
        return model.names[result.probs.top1]


Classification()
# Classification.GetMarkParallel('./1.jpg')
