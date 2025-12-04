# -*- coding: utf-8 -*-

'''
Unlike parameters.py on the raspberry pi, this does not seem to change the experiment folders' names after we run main, hence
useful_codes.py
'''

# stuff you shouldn't change
cropping_par = [206, 206, 100, 130]

GPIO = {'Red' : 7 }

camera_par = {'Res':[[],[550,550],[412,412]], 'Framerate':20}
tracking_par = {'Tracking_thr':40, 'Dist_thr':10, 'Backgroung_init':{'fps':40,'size_array':1}}

# stuff specific to your experiment 
larva_size = 3 # larva's age: put 2 for 2-day old larva (second instar), 1 for first instar, 3 for third instar.
# 17 cm between camera and maze base(Bottom)


par_test = {'Nb_choices':6,
                }

red_light = {'Wavelength':'650nm','Intensity':'150uWcm2','Voltage':'15V' }


exp_protocol = [['test',par_test]]

# Experiment Name 
genotype = 'EmptySSplit'

seed = 1   #From Seeds

odor = {'Odor' : 'Ethyl Acetate', 'Concentration' : '10-2', 'Seed' : seed, 'Volume':'1.5mul', 'Volume' : '1.5m2'}