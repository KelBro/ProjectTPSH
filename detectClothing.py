from ultralytics import YOLO
import threading
import cv2
from PIL import Image
from transformers import YolosForObjectDetection, YolosImageProcessor 
import torch

class Classification():
    def __init__(self):
        self.mdp = 'best.pt'
        Classification.DetFature_extractor = YolosImageProcessor.from_pretrained('./det')
        Classification.DetModel =  YolosForObjectDetection.from_pretrained('./det')
        Classification.cats = ['shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 
                               'vest', 'pants', 'shorts', 'skirt', 'coat', 'dress', 'jumpsuit', 'cape', 'glasses', 'hat', 'headband, head covering, hair accessory', 
                               'tie', 'glove', 'watch', 'belt', 'leg warmer', 'tights, stockings', 'sock', 'shoe', 'bag, wallet', 'scarf', 'umbrella', 'hood', 'collar', 
                               'lapel', 'epaulette', 'sleeve', 'pocket', 'neckline', 'buckle', 'zipper', 'applique', 'bead', 'bow', 'flower', 'fringe', 'ribbon', 'rivet', 'ruffle', 'sequin', 'tassel']
        print('fr')
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
        print(''.join(['=' for _ in range(53)])+'\n==- System message -====- thank that you chose us -==\n'+''.join(['=' for _ in range(53)]))
        

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
            try: detail = Classification.DetailModel.predict(imgPath)[0]
            except Exception as e: 
                print(e) 
                detail = None
        def ffabric():
            global fabricE
            try: fabricE = Classification.fabricElasticityModel.predict(imgPath)[0]
            except: fabricE = None 
        def ffit():
            global fit
            try: fit = Classification.fitClasses.predict(imgPath)[0]
            except: fit =None
        def fhemline():
            global hemline
            try: hemline = Classification.HemlineModel.predict(imgPath)[0]
            except: hemline = None
        def fmaterial():
            global material
            try: material = Classification.MaterialModel.predict(imgPath)[0]
            except: material =None
        def fneckline():
            global neckline
            try: neckline = Classification.NecklineModel.predict(imgPath)[0]
            except: neckline = None  
        def fpattern():
            global pattern
            try: pattern = Classification.PatternModel.predict(imgPath)[0]
            except: pattern = None  
        def fstyle():
            global style
            try: style = Classification.StyleModel.predict(imgPath)[0]
            except: style = None
        def ftypet():
            global typet
            try: typet = Classification.typeModel.predict(imgPath)[0]
            except: typet =None
            #os._exit(0)
        def fwaistline():
            global waistline
            try: waistline = Classification.WaistLineModel.predict(imgPath)[0]
            except: waistline = None

        #         cv2.imwrite("./1im.jpg", img)
        y1 = 10000000000000
        y2 = 0
        x1 = 10000000000000 
        x2 = 0
        x = []
        y =[]
        print("is the photo?")
        image = Image.open(open(imgPath, "rb")).resize((600, 800))

        inputs = Classification.DetFature_extractor(images=image, return_tensors="pt")
        outputs = Classification.DetModel(**inputs)

        wg , hg = image.size
        ts = torch.tensor([(hg,wg)])

        res = Classification.DetFature_extractor.post_process_object_detection(outputs=outputs, threshold=0.5, target_sizes=ts)[0]
        do = []
        stl = False
        pr = False
        pt = False
        for score, label, box in zip(res["scores"], res["labels"], res['boxes']):
            do.append(
                {
                    "label":Classification.cats[label],
                    "score": float(score),
                    "box": {
                        "xmin":int(box[0]),
                        "ymin":int(box[1]),
                        "xmax":int(box[2]),
                        "ymax":int(box[3])
                    }
                }
            )
        for i in do:
            chance = i['score']
            n = i['label']
            if n == 'pants':
                pr = True
            if n == 'dress':
                pt = True
            if n in ['shirt, blouse', 'top, t-shirt, sweatshirt', 'sweater', 'cardigan', 'jacket', 'vest', 'skirt', 'coat', 'dress', 
                     'jumpsuit', 'cape', 'leg warmer', 'hood', 'lapel', 'epaulette', 'neckline']:
                if n == 'neckline':
                    if chance > 0.8:
                        stl = True
                else:
                    stl = True
            print(f'chance that it is {n} is {int(chance*100)}%')
            x.append(i['box']['xmin'])
            y.append(i['box']['ymin'])
            x.append(i['box']['xmax'])
            y.append(i['box']['ymax'])
        if pr and not pt:
            stl = False
        if not stl:
            print('it not a dress')
            return {'department':'it not a dress'}
        print("it's photo")
        try:
            img = image.crop((min(x)-15,min(y)-15,max(x)+15,max(y)+15))
        except:
            img = image.crop((min(x),min(y),max(x),max(y)))
        img.save('./1im.jpg')
        imgPath  = "./1im.jpg"
    
        fs = [ftypet, fwaistline, fstyle, fpattern, fneckline, fmaterial, fhemline, ffit, ffabric, fdetail, fcolor]
        
        for i in range(len(fs)):
            exec(f'p{i} = threading.Thread(target = fs[{i}]())')
        for i in range(len(fs)):
            exec(f'p{i}.start()')
        for i in range(len(fs)):
            exec(f'p{i}.join()')
        a= {'department':'dress',
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
        print(str(a))
        return a

    def GetMarkNotParallel(imgPath):
        a = Classification.DetectModel(imgPath)
        asw = set([a[0].names[int(cls)] for cls in a[0].boxes.cls])
        if 'clothing' not in str(asw):
            return {'department':'it not a dress'}
        
        try: color = Classification.ColorModel.predict(imgPath)[0]
        except: color = None
        # department = Model.predict(imgPath)[0] # always is dress
        try: detail = Classification.DetailModel.predict(imgPath)[0]
        except: detail = None
        try: fabricE = Classification.fabricElasticityModel.predict(imgPath)[0]
        except: fabricE = None
        try: fit = Classification.fitClasses.predict(imgPath)[0]
        except: fit =None
        try: hemline = Classification.HemlineModel.predict(imgPath)[0]
        except: hemline = None
        try: material = Classification.MaterialModel.predict(imgPath)[0]
        except: material =None
        try: neckline = Classification.NecklineModel.predict(imgPath)[0]
        except: neckline = None
        try: pattern = Classification.PatternModel.predict(imgPath)[0]
        except: pattern = None
        try: style = Classification.StyleModel.predict(imgPath)[0]
        except: style = None
        try: typet = Classification.typeModel.predict(imgPath)[0]
        except: typet =None
        try: waistline = Classification.WaistLineModel.predict(imgPath)[0]
        except: waistline = None


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
