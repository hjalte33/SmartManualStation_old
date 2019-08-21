from pick_box import PickBox
from time import sleep
import yaml
import warnings

boxes = {}

with open('pin_config.yaml','r') as yamlfile:
    cfg = yaml.load(yamlfile)

for box, args in cfg.items():
    try:
        new_box = PickBox(box_id = box, led_pin = args['led_pin'], pir_pin = args['pir_pin'])
        if all(k in args for k in ('content_id','content_count')) :
            new_box.set_content(args['content_id'],args['content_count'])
        boxes[box] = new_box
    except KeyError as key:
        warnings.warn('The box id "%s" does not have the mandatorry key %s. The entry is skiped' %(box, key))

print(boxes)
sleep(5)
#my_box = PickBox(pir_pin = 17, led_pin = 18)
#my_box.select()

