import numpy as np
import pandas as pd

from opentrons import types

metadata = {
    'protocolName': 'HTGAA Robotic Patterning',
    'author': 'HTGAA',
    'source': 'HTGAA 2022',
    'apiLevel': '2.9'
}

def run(protocol):

  ##############################################################################
  ###   Load labware, modules and pipettes
  ##############################################################################

  # Tips
  tips_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', 6, 'Opentrons 20uL Tips')

  # Modules
  temperature_module = protocol.load_module('temperature module gen2', 1)

  # Temperature Module Plate
  temp_plate = temperature_module.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', label='Cold Plate')

  # Agar Plate
  agar_plate = protocol.load_labware('htgaa_agar_plate', 3, 'Agar Plate')  ## TA MUST CALIBRATE EACH PLATE!

  # Pipettes
  pipette_20ul = protocol.load_instrument("p20_single_gen2", "right", tip_racks=[tips_20ul])


  ##############################################################################
  ###   Configure starting tips 
  ##############################################################################

  pipette_20ul.starting_tip = tips_20ul.well('A1')   ## CHANGE ME

  ##############################################################################
  ###   Patterning
  ##############################################################################

  # Replace the code below with your pattern
  
  # Get the top-center of the plate, make sure the plate was calibrated before running this
  center_location = agar_plate['A1'].top()

  # Choose where to take the colors from
  input_plate = temp_plate

  #Gets the coordinates of my design, so that they can be read into the protocol
  url = 'https://ganitgold.github.io/pattern/2colors.CSV'
  world_coord = pd.read_csv(url)
  data = world_coord
  data [['x', 'y','z']] = data ['Object Type'].str.split(',', 2, expand=True)
  data ['x'] = data ['x'].astype(float)
  data ['y'] = data ['z'].astype(float)
  data ['z'] = data ['z'].astype(float)
  group = data ['Group Indexes'].astype (int)
  print (data)
  


  #Inverts the y-coordinates, else my design is upside-down
  y_inverted = np.amax(data['y'])-data['y']

  #Get min and max x-/y-values from my coordinates
  raw_x_min = np.amin(data['x'])
  raw_x_max = np.amax(data['x'])
  raw_y_min = np.amin(y_inverted)
  raw_y_max = np.amax(y_inverted)


  #Shift data, so that the centerpoint 0/0 is at the center of my design 
  world_coord_x_shifted = data['x']-((raw_x_min + raw_x_max)/2)
  world_coord_y_shifted = y_inverted-((raw_y_min + raw_y_max)/2)

  all_distances_to_center = np.sqrt(np.square(world_coord_x_shifted) + np.square(world_coord_y_shifted));

  world_coord_x_85mm_shifted = 40/np.amax(all_distances_to_center)*world_coord_x_shifted;
  world_coord_y_85mm_shifted = 40/np.amax(all_distances_to_center)*world_coord_y_shifted;

  #Opentron Protocol for a pink microbial earth

  # Get the top-center of the plate, make sure the plate was calibrated before running this
  
  center_location = agar_plate['A1'].top() 

  purple = input_plate['A1'] #Change to location of pink transformands
  blue = input_plate['A2']

  # Aspirate
  pipette_20ul.pick_up_tip()


  i=0
  while i < len(world_coord_x_85mm_shifted):
    if group [i] == 21 : 
      break
    if i % 20 == 0:
      #pick up more every 20 uL

      pipette_20ul.aspirate(20, blue)


    adjusted_location = center_location.move(types.Point(world_coord_x_85mm_shifted[i], world_coord_y_85mm_shifted[i]))
    pipette_20ul.dispense(1, adjusted_location) 
    hover_location = adjusted_location.move(types.Point(z = 2))
    pipette_20ul.move_to(hover_location)
    i+=1


  pipette_20ul.drop_tip()

  while i < len(world_coord_x_85mm_shifted):
    if group [i] == 18 : 
      break
    if i % 20 == 0:
      #pick up more every 20 uL

      pipette_20ul.aspirate(20, purple)


    adjusted_location = center_location.move(types.Point(world_coord_x_85mm_shifted[i], world_coord_y_85mm_shifted[i]))
    pipette_20ul.dispense(1, adjusted_location) 
    hover_location = adjusted_location.move(types.Point(z = 2))
    pipette_20ul.move_to(hover_location)
    i+=1

  pipette_20ul.drop_tip()
