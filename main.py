from pick_box import PickBox
from time import sleep
import yaml

with open('pin_config.yaml','r') as yamlfile:
    cfg = yaml.load(yamlfile)

for box, pins in cfg.:
    print(box, pins)

#my_box = PickBox(pir_pin = 17, led_pin = 18)
#my_box.select()

