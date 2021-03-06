
import dlib
from skimage import io
import math

from core.model import FacialFeatures

# temp
import cv2

class FaceLandmarkDetector(object):
    def __init__(self, path):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(path)

        # remove this later - start

        # testing_files_list = ["073A16", "072A19", "072A45", "076A14", "082A20", "080A08", "077A07"]
        # for img in testing_files_list:
        #     input_img = cv2.imread("data/datatang/test/" + img + ".JPG")
        #     # input_img = cv2.imread("data/test-images/" + img + ".JPG")
        #     height, width, channels = input_img.shape
        #     aspect_ratio = 1.0 * width / height
        #     new_width = 400
        #     new_height = int(new_width / aspect_ratio)
        #     resized_img = cv2.resize(input_img, (new_width, new_height))
        #     gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

        #     detections = self.detector(resized_img, 1)
        #     for k,d in enumerate(detections):
        #         shape = self.predictor(input_img, d)
        #         feature_dict = self.parseShape(shape)

        #     names = "jaw left_brow right_brow nose_unnecessary nose left_eye right_eye lips lips_divider".split()
        #     for name in names:
        #         for i in range(0,len(feature_dict[name])):
        #         	cv2.circle(resized_img, feature_dict[name][i], 2 , (255,0,255), -1)

        #     cv2.imshow("Detected boundary pixels", resized_img)
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()
        # exit()
        
        # remove this later - end

    def detect(self, image):
        detections = self.detector(image, 1)
        for k,d in enumerate(detections):
            shape = self.predictor(image, d)
            feature_dict = self.parseShape(shape)
            ratios = self.calculate_ratios(feature_dict)
            face_boundary = self.calculate_face_boundary_angles(feature_dict)
            yield FacialFeatures(ratios=ratios,
                    feature_points=feature_dict,
                    face_boundary=face_boundary,
                    all_points=shape)

    def parseShape(self, shape):
        ranges = [range(0,17), range(17,22), range(22,27), range(28,31),
                range(31,36),  range(36,42), range(42,48), range(48,60), range(61,68)]

        names = "jaw left_brow right_brow nose_unnecessary nose left_eye right_eye lips lips_divider".split()
        s = lambda x: (x.x, x.y)
        return {k: [s(shape.part(i)) for i in indices] 
                        for k, indices in zip(names,ranges)}

    def calculate_ratios(self, feature_dict):
        ratios = {}
        names = "facial_ind mandibular_ind intercanthal_ind orbital_width_ind eye_fissure_ind \
                    nasal_ind vermillion_height_ind mouth_face_width_ind".split()

        third_eye_x = feature_dict["left_brow"][0][0] + feature_dict["right_brow"][-1][0] + \
         feature_dict["left_brow"][-1][0] + feature_dict["right_brow"][0][0]
        third_eye_y = feature_dict["left_brow"][0][1] + feature_dict["right_brow"][-1][1] + \
         feature_dict["left_brow"][-1][1] + feature_dict["right_brow"][0][1]
         

        feature_dict["third_eye"] = [(third_eye_x/4,third_eye_y/4)]
        
        ratios[names[0]] = self.distance_ratio(feature_dict,"third_eye",0,"jaw",8,"jaw",1,"jaw",-2)
        ratios[names[1]] = self.distance_ratio(feature_dict,"lips_divider",1,"jaw",8,"jaw",5,"jaw",11)
        ratios[names[2]] = self.distance_ratio(feature_dict,"left_eye",3,"right_eye",0,"left_eye",0,"right_eye",3)
        ratios[names[3]] = self.distance_ratio(feature_dict,"left_eye",0,"left_eye",3,"left_eye",3,"right_eye",0)
#        ratios[names[4]] = self.distance_ratio(feature_dict,"left_eye",,"left_eye",,"left_eye",0,"left_eye",3)
        ratios[names[5]] = self.distance_ratio(feature_dict,"nose",0,"nose",-1,"third_eye",0,"nose",2)
        ratios[names[6]] = self.distance_ratio(feature_dict,"lips",3,"lips_divider",1,"lips_divider",-2,"lips",9)
        ratios[names[7]] = self.distance_ratio(feature_dict,"lips",0,"lips",6,"jaw",1,"jaw",-2)
        

        return ratios

    def distance_ratio(self, feature_dict, num_f1,num_i1, num_f2,num_i2, den_f1,den_i1, den_f2,den_i2):
    	num = (feature_dict[num_f1][num_i1][0] - feature_dict[num_f2][num_i2][0]) ** 2 \
    			+ (feature_dict[num_f1][num_i1][1] - feature_dict[num_f2][num_i2][1]) ** 2

    	den = (feature_dict[den_f1][den_i1][0] - feature_dict[den_f2][den_i2][0]) ** 2 \
    			+ (feature_dict[den_f1][den_i1][1] - feature_dict[den_f2][den_i2][1]) ** 2
    	return math.sqrt(num * 1.0 / den)



    def calculate_face_boundary_angles(self, feature_dict):
        angles_with_x_axis = self.find_angles(feature_dict["jaw"]) #gives angles that each point makes with the x-axis
        
        angles = []
        for i in range(1,15):
            angles.append(angles_with_x_axis[i+1] + math.pi - angles_with_x_axis[i])
        
        return angles

    def find_angles(self, jaws):
        theta = [0]
        for i in range(0,15):
            theta.append(self.angle_between(jaws[i], jaws[i+1]))
        return theta
    
    def angle_between(self, p1, p2):
        if p2[0]-p1[0] == 0:
            if p2[1]>p1[1]:
                return math.pi/2
            return -math.pi/2
        return math.atan((p2[1]-p1[1])/(p2[0]-p1[0]))

