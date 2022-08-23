import pygame
import pandas as pd
import os
import random
from copy import deepcopy


# scales the image (be default all my images are HUGE, so the window doesn't even fit on screen
# this is just a func to scale imgs by some given factor so fit on my display
def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


# I don't think map_range is being used rn, but it generally a useful function and i may end up using it in calc_stats
def map_range(input, in_min, in_max, out_min, out_max):
    slope = (out_max - out_min) / (in_max - in_min)
    return out_min + slope * (input - in_min)


def initialize():
    # get path to the python script being run (this file)
    dirname = os.path.dirname(__file__)
    # read in csv of clothes data and store in pandas dataframe
    df = pd.read_csv(os.path.join(dirname, '../Assets/directory.csv'))
    # read in layer info csv and store in pandas dataframe
    layer_info_df = pd.read_csv(os.path.join(dirname, '../Assets/layer_info.csv'))

    # setting scale
    SCALE = 4.0
    # loading background image
    BACKGROUND_IMG = pygame.image.load(os.path.join(dirname, '../Assets/BACKGROUND.png'))
    BACKGROUND_IMG = scale_img(BACKGROUND_IMG, SCALE)

    # initializing pygame window
    FPS = 60
    WIDTH = BACKGROUND_IMG.get_width()
    HEIGHT = BACKGROUND_IMG.get_height()
    TITLE = "Paper Amelia"
    FONTNAME = 'comicsans'
    FONTSIZE = 24
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    pygame.font.init()
    my_font = pygame.font.SysFont(FONTNAME, FONTSIZE)

    # setting some defaults
    SHOW_GUI = True
    SHOW_HELP = False
    SHOW_STATS = False
    axis_key = ['total_coverage', 'weight', 'avg_thickness', 'avg_breathability', 'waterproof', 'avg_brightness',
                'sportiness', 'formality', 'loungeablity', 'warmth']
    OP_AXIS = 7
    OP_AXIS_MAX = True
    LOAD_DEFAULT = True

    # getting some info
    num_layers = layer_info_df.shape[0]
    active_layer = 1
    active_item = [0] * num_layers

    num_items = [0] * num_layers
    for layer in range(num_layers):
        num_items[layer] = len(df[df.layer == layer])

    outfit = [None] * num_layers
    for layer in range(num_layers):
        for x in range(len(num_items)):
            outfit[layer] = [False] * num_items[layer]
    outfit[0][0] = True

    locked = [False] * num_layers

    if LOAD_DEFAULT:
        default_df = pd.read_csv(os.path.join(dirname, '../Assets/default.csv'))
        for index, row, in default_df.iterrows():
            outfit[row['layer']][row['item_index']] = True
            active_item[row['layer']] = row['item_index']

    sprites = [None] * df.shape[0]
    # append column for sprites to the clothes dataframe
    df = df.assign(Sprite=sprites)

    context = {
        "dataframe": df,
        "outfit": outfit,
        "active_layer": active_layer,
        "active_item": active_item,
        "num_items": num_items,
        "locked": locked,
        "dirname": dirname,
        "layer_info_df": layer_info_df
    }

    overlay_toggles = {
        "SHOW_GUI": SHOW_GUI,
        "SHOW_HELP": SHOW_HELP,
        "SHOW_STATS": SHOW_STATS
    }

    drawing_context = {
        "screen": screen,
        "clock": clock,
        "FPS": FPS,
        "SCALE": SCALE,
        "BACKGROUND_IMG": BACKGROUND_IMG,
        "WIDTH": WIDTH,
        "HEIGHT": HEIGHT,
        "my_font": my_font,
        "axis_key": axis_key
    }

    optimization_context = {
        "OP_AXIS": OP_AXIS,
        "OP_AXIS_MAX": OP_AXIS_MAX
    }
    return context, overlay_toggles, drawing_context, optimization_context


def shuffle(context, alt_outfit=None):
    # these won't be modified
    outfit = context['outfit']
    locked = context['locked']
    num_items = context['num_items']
    layer_info_df = context['layer_info_df']

    num_layers = layer_info_df.shape[0]

    # shuffle the current outfit by default
    working_outfit = outfit
    if alt_outfit is not None:  # otherwise shuffle the given alternate outfit
        working_outfit = alt_outfit

    # go through all the layers
    for l in range(num_layers):
        # if the layer is locked, skip it
        if locked[l]:
            continue
        # if the layer is 0 (base) skip it
        if l == 0:
            continue

        # turn off all items in this layer
        copy = working_outfit[l]
        for x in range(len(copy)):
            copy[x] = False
        working_outfit[l] = copy

        # pick a random item on this layer to make active
        r = random.randrange(0, num_items[l])
        # some percent chance we leave all items in this layer off
        if random.randrange(0, num_items[l] * 10) <= 5:
            continue
        working_outfit[l][r] = True
    return working_outfit.copy()


def minor_shuffle(context, z, k, s=None):  # z is the layer, k is the item index, s is alt outfit
    # these won't be modified
    outfit = context['outfit']
    locked = context['locked']
    num_items = context['num_items']

    # if this layer is locked, stop, don't make any changes, return current outfit
    if locked[z]:
        return outfit
    # operate on copt of current outfit, unless alt_outfit is passed in
    outfit_copy = deepcopy(outfit)
    if s is not None:
        outfit_copy = s

    # turn off all items in that layer
    copy = outfit_copy[z]
    for x in range(len(copy)):
        copy[x] = False
    outfit_copy[z] = copy

    # if the index we are going to turn on is invalid range, return current outfit with this layer turned completely off
    # this is used. sometimes we pass in the index +1 so that we can see if no items improves the score more
    # than any real item in the list
    if k > num_items[z] - 1:
        return outfit_copy

    # otherwise we return the outfit with the selected item turned on (and that is all that is on in the given layer)
    outfit_copy[z][k] = True
    return outfit_copy


def major_optimize(context, drawing_context, optimization_context, max_iterations):
    # context
    outfit = context['outfit']
    active_item = context['active_item']

    # drawing context
    # these won't be modified
    screen = drawing_context['screen']
    WIDTH = drawing_context['WIDTH']
    HEIGHT = drawing_context['HEIGHT']

    # optimization context
    OP_AXIS = optimization_context["OP_AXIS"]
    OP_AXIS_MAX = optimization_context["OP_AXIS_MAX"]

    # draw red circle in corner to indicate processing
    pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 20, 20), 10)
    pygame.display.update()

    # get score for current outfit / set it to max score / save current outfit
    stats = calc_stats(context)
    max_score = stats[OP_AXIS]

    save_outfit = deepcopy(outfit)

    # we will randomly shuffle the outfit 'max_iterations' times
    for i in range(max_iterations):
        # get new random outfit / score it
        new_outfit = shuffle(context, deepcopy(outfit))
        stats = calc_stats(context, new_outfit)
        new_score = stats[OP_AXIS]
        # if new score is better than what we had previously
        # then we update the current outfit to be that new 'best outfit'
        # and we break out. stopping all further iterations
        # (we only find the next random outfit that is better than what we currently have)
        if OP_AXIS_MAX:  # if trying to maximize the score
            if new_score > max_score:
                save_outfit = deepcopy(new_outfit)
                outfit = deepcopy(save_outfit)
                context['outfit'] = outfit
                # draw new best outfit
                display(context, drawing_context)
                pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 20, 20), 10)
                pygame.display.update()
                break
        else:  # if trying to minimize
            if new_score < max_score:
                save_outfit = deepcopy(new_outfit)
                outfit = deepcopy(save_outfit)
                context['outfit'] = outfit
                # draw new best outfit
                display(context, drawing_context)
                pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 20, 20), 10)
                pygame.display.update()
                break
    # assign the best found outfit to be current outfit
    outfit = deepcopy(save_outfit)
    # update current item index
    for l in range(len(outfit)):
        for a in range(len(outfit[l])):
            if outfit[l][a]:
                active_item[l] = a
                context['active_item'] = active_item
    context['outfit'] = outfit


def multi_opt(context, drawing_context, optimization_context, axis_array, iterations):
    # this whole function is sort of a WIP (it's not used anywhere)
    # the idea is to be able to optimize on multiple axes
    # basically it only modifies one random piece of clothing at a time, on a specific axis determined by
    # the axis_weights array (higher weights mean that axis is chosen more often)
    # if we do this enough times, then hopefully the random alterations will approach stats with agreeable values
    # taht is the idea anyway

    # axis_key = ['total_coverage', 'weight', 'avg_thickness', 'avg_breathability', 'waterproof', 'avg_brightness', 'sportiness', 'formality', 'loungeablity', 'warmth']
    # ex. winter condition
    # axis_array_weights = [0.9, 0.5, 0.8, 0.4, 0.2, 0.6, 0.1, 0.0, 0.15, 0.99]
    # axis_array_maxs = [True, True, True, False, True, False, True, True, True, True]
    # ex. summer condition
    axis_array_weights = [0.5,   0.2,    0.6,    0.8,    0.1,    0.5,    0.45,   0.4,    0.15,   0.99]
    axis_array_maxs =    [False, False,  False,  True,   True,   True,   True,   True,   True,   False]

    index_array = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(round(iterations)):
        ind = random.choices(index_array, weights=axis_array_weights, k=1)
        optimization_context['OP_AXIS'] = index_array[ind[0]]
        optimization_context['OP_AXIS_MAX'] = axis_array_maxs[ind[0]]
        context = minor_optimize(context, drawing_context, optimization_context, 1, rand=True)


def minor_optimize(context, drawing_context, optimization_context, iterations, rand=False):
    # context
    outfit = context['outfit']
    active_item = context['active_item']
    # these won't be modified
    num_items = context['num_items']
    layer_info_df = context['layer_info_df']

    # drawing context
    # these won't be modified
    screen = drawing_context['screen']
    WIDTH = drawing_context['WIDTH']
    HEIGHT = drawing_context['HEIGHT']

    # optimization context
    OP_AXIS = optimization_context["OP_AXIS"]
    OP_AXIS_MAX = optimization_context["OP_AXIS_MAX"]

    num_layers = layer_info_df.shape[0]
    
    # we draw a small blue indicator in the corner of the screen to indicate the program is processing
    pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
    pygame.display.update()

    # get metrics for current outfit
    stats = calc_stats(context)
    prev_score = stats[OP_AXIS]  # save the score on the field we are interested in optimizing (prev best)

    similarity_counter = 0

    # original outfit stored in save_outfit
    save_outfit = deepcopy(outfit)
    
    # we loop through each item on each layer to see if any one item can provide a better score
    # if an item improves the score we save that as new prev best, and update current outfit to be the 'winning outfit'
    # continue for given number of iterations
    # (we go through the layers in order, and the items on each layer in order, but
    # always start in random spots in those lists)
    for i in range(iterations):
        # operate on 'next layer', try next article of clothing
        layer_op = (i % (num_layers - 1)) + 1
        if rand:  # if rand we operate on a completely random layer
            r = random.randrange(0, (num_layers - 1))
            layer_op = ((i+r) % (num_layers - 1)) + 1
        item_op_offset = random.randrange(0, num_items[layer_op] + 1)

        # go through each item on this layer
        for j in range(num_items[layer_op] + 1):
            item_op = ((j+item_op_offset) % (num_items[layer_op] + 1))

            # minor shuffle doesn't really shuffle
            # it just turns off everything in this layer, then turns on the specified item index (item_op)
            new_outfit = minor_shuffle(context, layer_op, item_op, deepcopy(outfit))
            stats = calc_stats(context, new_outfit)
            new_score = stats[OP_AXIS]

            # if new score is better, new score is prev best / save this outfit as new current outfit
            if OP_AXIS_MAX:  # if we are trying to maximize the score
                if new_score > prev_score:
                    prev_score = new_score
                    save_outfit = deepcopy(new_outfit)
                    outfit = deepcopy(new_outfit)
                    context['outfit'] = outfit
                    # draw this new better outfit on screen
                    display(context, drawing_context)
                    pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
                    pygame.display.update()
            else:  # if we are trying to minimize the score
                if new_score < prev_score:
                    prev_score = new_score
                    save_outfit = deepcopy(new_outfit)
                    outfit = deepcopy(new_outfit)
                    context['outfit'] = outfit
                    # draw this new better outfit on screen
                    display(context, drawing_context)
                    pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
                    pygame.display.update()

        # if our current outfit is the same as the previous outfit add 1 to the similarity counter
        if outfit == save_outfit:
            similarity_counter += 1
        else:
            similarity_counter = 0  # if it differs, reset similarity to 0

        # if the similarity counter reaches a certain threshold (we have had the same outfit for so many iterations
        # without any improvements) then we stop searching and say we are optimized
        if similarity_counter >= num_layers * 3:
            # this stuff (for loop) just sets the active items to be the same as what is on the current outfit
            for l in range(len(outfit)):
                for a in range(len(outfit[l])):
                    if outfit[l][a]:
                        active_item[l] = a
                        context['active_item'] = active_item
            return
    # assign the best found outfit to be current outfit
    outfit = deepcopy(save_outfit)
    # this stuff (for loop) just sets the active items to be the same as what is on the current outfit
    for l in range(len(outfit)):
        for a in range(len(outfit[l])):
            if outfit[l][a]:
                active_item[l] = a
                context['outfit'] = outfit

    # save the outfit we found to be the current outfit in the context
    context['outfit'] = outfit
    return


def calc_stats(context, alt_outfit=None):
    # context
    # these won't be modified
    df = context['dataframe']
    outfit = context['outfit']
    layer_info_df = context['layer_info_df']

    num_layers = layer_info_df.shape[0]

    # we calculate the stats of out current outfit by default
    working_outfit = outfit
    if alt_outfit is not None:  # if an alternate outfit is passed in we calculate its stats instead
        working_outfit = alt_outfit

    # initializing stats
    n_clothes = 0
    total_coverage = 0
    weight = 0
    avg_thickness = 0
    avg_breathability = 0
    avg_brightness = 0
    avg_waterproofing = 0
    sportiness = 0
    formality = 0
    loungeablity = 0
    warmth = 0

    for l in range(num_layers):
        items_in_layer = df[df.layer == l]
        for i in range(len(working_outfit[l])):
            if working_outfit[l][i]:  # if current item we are looking at is turned ON
                n_clothes += 1
                # get stats on this article
                row = items_in_layer.iloc[i]
                coverage = row['coverage']
                thickness = row['thickness']
                breathability = row['breathability']
                waterproofing = row['waterproofing']

                total_coverage += coverage
                weight += row['weight(kg)']
                avg_thickness += thickness
                avg_breathability += (1.0 - breathability)

                sportiness += row['sportiness']
                formality += row['formality']
                loungeablity += row['loungeablity']

                avg_waterproofing += coverage * waterproofing
                avg_brightness += coverage * row['brightness']
                warmth += coverage * ((thickness + (1.0 - breathability) + (-avg_brightness*0.30)) / 3)
    # do some wierd math, idk, should prob think about this more
    if num_layers != 0 and n_clothes != 0:
        avg_thickness = (avg_thickness / (num_layers - 1)) * 100.00
        avg_breathability = 100.00 - ((avg_breathability / (num_layers-1)) * 100.00)
        sportiness = (sportiness / (num_layers-1)) * 100.00
        formality = (formality / (num_layers-1)) * 100.00
        loungeablity = (loungeablity / (num_layers-1)) * 100.00

        avg_waterproofing = (100.00 * avg_waterproofing) / total_coverage
        avg_brightness = (100.00 * avg_brightness) / total_coverage
        warmth = (100.00 * warmth) / total_coverage
    # should probably return this as a dictionary
    return (
    total_coverage, weight, avg_thickness, avg_breathability, avg_waterproofing, avg_brightness, sportiness, formality,
    loungeablity, warmth)


def display(context, drawing_context, alt_outfit=None):
    # context
    df = context['dataframe']
    # these won't be modified
    outfit = context['outfit']
    num_items = context['num_items']
    dirname = context['dirname']
    layer_info_df = context['layer_info_df']

    # drawing context
    # these won't be modified
    screen = drawing_context['screen']
    SCALE = drawing_context['SCALE']
    BACKGROUND_IMG = drawing_context['BACKGROUND_IMG']

    num_layers = layer_info_df.shape[0]

    # working outfit is the outfit we will draw
    working_outfit = outfit  # by default, it is our current outfit
    if alt_outfit is not None:  # if a different outfit is specified we draw that instead
        working_outfit = alt_outfit

    # draw BG
    screen.blit(BACKGROUND_IMG, (0, 0))  # draw BG

    # display character
    for layer in range(num_layers):
        # if there are no items in this layer continue
        if num_items[layer] == 0:
            continue

        # get a list (pandas) of all items in this layer
        items_in_layer = df[df.layer == layer]

        # Go through each item in this layer...
        # if this item is turned on, then draw it
        # (we render to the buffer, but no flip occurs in this function)
        for i in range(len(working_outfit[layer])):
            if working_outfit[layer][i]:
                row = items_in_layer.iloc[i]
                # load in img if need be
                if row['Sprite'] is None:
                    print('Loading img: ', row['img_name'], ' ...')
                    s = pygame.image.load(os.path.join(dirname, '../Assets/' + str(row['img_name'])))
                    s = scale_img(s, SCALE)
                    row['Sprite'] = s
                    # add the sprite to the actual dataframe
                    real_row_index = df.index[df['img_name'] == row['img_name']].tolist()[0]
                    df.at[real_row_index, 'Sprite'] = s
                    context['dataframe'] = df
                screen.blit(row['Sprite'], (row['x'], row['y']))


def draw_overlay(context, overlay_toggles, drawing_context):
    # context
    df = context['dataframe']
    # these won't be modified
    outfit = context['outfit']
    active_layer = context['active_layer']
    active_item = context['active_item']
    locked = context['locked']
    num_items = context['num_items']
    dirname = context['dirname']
    layer_info_df = context['layer_info_df']

    # toggle overlays context
    # these won't be modified
    SHOW_GUI = overlay_toggles["SHOW_GUI"]
    SHOW_HELP = overlay_toggles["SHOW_HELP"]
    SHOW_STATS = overlay_toggles["SHOW_STATS"]

    # drawing context
    # these won't be modified
    screen = drawing_context['screen']
    SCALE = drawing_context['SCALE']
    WIDTH = drawing_context['WIDTH']
    HEIGHT = drawing_context['HEIGHT']
    my_font = drawing_context['my_font']

    if SHOW_HELP:
        help_text = ['x -> remove all items on layer',
                     'CTRL+X -> remove all items',
                     'y -> hide character',
                     'g -> toggle GUI',
                     'left/right -> switch layers',
                     'up/down -> switch item in layer',
                     'return -> toggle item on/off',
                     'h -> toggle help',
                     'CTRL+S -> save screenshot',
                     'r -> shuffle to random outfit',
                     't -> show stats',
                     'm -> random step optimization',
                     'n -> systematic optimization',
                     'o -> open optimization menu',
                     'CTRL+L -> load all assets',
                     'l -> lock layer',
                     'u -> unlock layer']
        for i in range(len(help_text)):
            help_text_real = my_font.render(help_text[i], False, (255, 255, 255))
            screen.blit(help_text_real, (WIDTH / 2 - WIDTH * .25, HEIGHT / 2 - HEIGHT * .25 + (i * 25)))
    if SHOW_STATS:
        total_coverage, weight, avg_thickness, avg_breathability, avg_waterproofing, avg_brightness, sportiness, formality, loungeablity, warmth = calc_stats(context)

        stats = ['total coverage: ' + str(round(100.00 * total_coverage, 2)) + '%',
                 'weight: ' + str(round(weight, 2)) + '(kg)',
                 'avg thickness: ' + str(round(avg_thickness, 2)) + '%',
                 'avg breathability: ' + str(round(avg_breathability, 2)) + '%',
                 'avg waterproofing: ' + str(round(avg_waterproofing, 2)) + '%',
                 'avg brightness: ' + str(round(avg_brightness, 2)) + '%',
                 'sportiness: ' + str(round(sportiness, 2)) + '%',
                 'formality: ' + str(round(formality, 2)) + '%',
                 'loungeablity: ' + str(round(loungeablity, 2)) + '%',
                 'warmth: ' + str(round(warmth, 2)) + '%']
        for i in range(len(stats)):
            stat_text = my_font.render(stats[i], False, (255, 255, 255))
            screen.blit(stat_text, (WIDTH / 2 - WIDTH * .25, 6 * HEIGHT / 7 - HEIGHT * .25 + (i * 28)))
    if SHOW_GUI:
        # show text status
        layer_name = layer_info_df.iloc[active_layer]['name']
        if locked[active_layer]:
            layer_name += ' (L)'
        layer_info = my_font.render('<-layer->: ' + layer_name, False, (255, 255, 255))
        screen.blit(layer_info, (20, 20))
        item_info = my_font.render('^itemv: ' + str(active_item[active_layer]), False, (255, 255, 255))
        screen.blit(item_info, (20, 50))
        if num_items[active_layer] != 0:
            item_info_on = my_font.render('status: ' + str(outfit[active_layer][active_item[active_layer]]),
                                          False,
                                          (255, 255, 255))
            screen.blit(item_info_on, (20, 80))
        # draw preview image of current item
        if num_items[active_layer] != 0:
            items_in_layer = df[df.layer == active_layer]  # all items in this layer
            cur_active_item = [active_item[active_layer]]  # currently selected item (index) on currently selected layer
            row = items_in_layer.iloc[cur_active_item]  # row in the df containing the currently selected item
            # if the selected item's sprite is not yet loaded... load it
            if row['Sprite'].values[0] is None:
                print('*Loading img: ', row['img_name'].values[0], ' ...')
                s = pygame.image.load(os.path.join(dirname, '../Assets/' + str(row['img_name'].values[0])))
                s = scale_img(s, SCALE)
                row['Sprite'] = s
                # add the sprite to the actual dataframe
                real_row_index = df.index[df['img_name'] == row['img_name'].values[0]].tolist()[0]
                df.at[real_row_index, 'Sprite'] = s
                context['dataframe'] = df
            # draw the item preview to the left of the model
            screen.blit(row['Sprite'].values[0], (row['x'].values[0] - (WIDTH * 0.3), row['y'].values[0]))


def check_events(context, overlay_toggles, drawing_context, optimization_context):
    # context
    df = context['dataframe']
    outfit = context['outfit']
    active_layer = context['active_layer']
    active_item = context['active_item']
    locked = context['locked']
    # these won't be modified
    num_items = context['num_items']
    dirname = context['dirname']
    layer_info_df = context['layer_info_df']

    # toggle overlays context
    SHOW_GUI = overlay_toggles["SHOW_GUI"]
    SHOW_HELP = overlay_toggles["SHOW_HELP"]
    SHOW_STATS = overlay_toggles["SHOW_STATS"]

    # drawing context
    # these won't be modified
    screen = drawing_context['screen']
    clock = drawing_context['clock']
    FPS = drawing_context['FPS']
    SCALE = drawing_context['SCALE']
    WIDTH = drawing_context['WIDTH']
    HEIGHT = drawing_context['HEIGHT']
    my_font = drawing_context['my_font']
    axis_key = drawing_context['axis_key']

    # optimization context
    OP_AXIS = optimization_context["OP_AXIS"]
    OP_AXIS_MAX = optimization_context["OP_AXIS_MAX"]

    num_layers = layer_info_df.shape[0]

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL):
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            # toggle GUI overlay
            if event.key == pygame.K_g:
                SHOW_GUI = not SHOW_GUI
                overlay_toggles["SHOW_GUI"] = SHOW_GUI
            # if GUI enabled
            if SHOW_GUI:
                # move left a layer
                if event.key == pygame.K_LEFT and SHOW_GUI:
                    active_layer = active_layer - 1
                    if active_layer < 1:
                        active_layer = 1
                    context['active_layer'] = active_layer
                # move right a layer
                if event.key == pygame.K_RIGHT and SHOW_GUI:
                    active_layer = active_layer + 1
                    if active_layer > (num_layers - 1):
                        active_layer = (num_layers - 1)
                    context['active_layer'] = active_layer
                # move up an item
                if event.key == pygame.K_UP and SHOW_GUI:
                    if num_items[active_layer] == 0:
                        break
                    active_item[active_layer] += 1
                    active_item[active_layer] = active_item[active_layer] % num_items[active_layer]
                    context['active_item'] = active_item
                #  move down an item
                if event.key == pygame.K_DOWN and SHOW_GUI:
                    if num_items[active_layer] == 0:
                        break
                    active_item[active_layer] -= 1
                    active_item[active_layer] = active_item[active_layer] % num_items[active_layer]
                    context['active_item'] = active_item
                # toggle item on/off
                if event.key == pygame.K_RETURN and SHOW_GUI:
                    outfit[active_layer][active_item[active_layer]] = not outfit[active_layer][active_item[active_layer]]
                    context['outfit'] = outfit
                # turn off all items in current layer
                if event.key == pygame.K_x:
                    copy = outfit[active_layer]
                    for x in range(len(copy)):
                        copy[x] = False
                    outfit[active_layer] = copy
                    context['outfit'] = outfit
            # turn off ALL items
            if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                for l in range(num_layers):
                    if l == 0:
                        continue
                    copy = outfit[l]
                    for x in range(len(copy)):
                        copy[x] = False
                    outfit[l] = copy
                    context['outfit'] = outfit
            # take a screenshot
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                print("SCREENSHOT")
                dir_path = os.path.join(dirname, '../Screenshots')
                count = 0
                for path in os.listdir(dir_path):
                    if os.path.isfile(os.path.join(dir_path, path)):
                        count += 1
                while os.path.exists(os.path.join(dirname, "../Screenshots/screenshot" + str(count) + ".png")):
                    count += 1
                pygame.image.save(screen, str(os.path.join(dirname, "../Screenshots/screenshot" + str(count) + ".png")))
            # load all unloaded assets
            if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                for i in range(num_layers):
                    items_in_layer = df[df.layer == i]  # all items in this layer
                    for j in range(num_items[i]):
                        row = items_in_layer.iloc[j]
                        # load in img if need be
                        if row['Sprite'] is None:
                            print('Loading img: ', row['img_name'], ' ...')
                            s = pygame.image.load(os.path.join(dirname, '../Assets/' + str(row['img_name'])))
                            s = scale_img(s, SCALE)
                            row['Sprite'] = s
                            # add the sprite to the actual dataframe
                            real_row_index = df.index[df['img_name'] == row['img_name']].tolist()[0]
                            df.at[real_row_index, 'Sprite'] = s
                context['dataframe'] = df
            # hide base
            if event.key == pygame.K_y:
                outfit[0][0] = not outfit[0][0]
                context['outfit'] = outfit
            # toggle help overlay
            if event.key == pygame.K_h:
                SHOW_HELP = not SHOW_HELP
                overlay_toggles["SHOW_HELP"] = SHOW_HELP
            # toggle stats overlay
            if event.key == pygame.K_t:
                SHOW_STATS = not SHOW_STATS
                overlay_toggles["SHOW_STATS"] = SHOW_STATS
            # randomize the current outfit (ignoring locked layers)
            if event.key == pygame.K_r:
                outfit = shuffle(context)
                for l in range(len(outfit)):
                    for a in range(len(outfit[l])):
                        if outfit[l][a]:
                            active_item[l] = a
                context['outfit'] = outfit
                context['active_item'] = active_item
            # optimize on the axis randomly
            if event.key == pygame.K_m:
                context = major_optimize(context, drawing_context, optimization_context, 1000)
            # optimize on the axis systematically
            if event.key == pygame.K_n:
                context = minor_optimize(context, drawing_context, optimization_context, 300)
            # lock the current layer
            if event.key == pygame.K_l:
                locked[active_layer] = True
                context['locked'] = locked
            # unlock current layer
            if event.key == pygame.K_u:
                locked[active_layer] = False
                context['locked'] = locked
            # open optimization menu
            if event.key == pygame.K_o:
                # optimization menu
                in_menu = True
                while in_menu:
                    # draw the BG and current outfit
                    display(context, drawing_context)
                    # draw menu
                    axis_text = '<-AXIS->: ' + str(axis_key[OP_AXIS])
                    max_text = '^MAXv: ' + str(OP_AXIS_MAX)
                    axis_text_real = my_font.render(axis_text, False, (255, 255, 255))
                    max_text_real = my_font.render(max_text, False, (255, 255, 255))
                    escape_real = my_font.render("Press 'o' to exit menu", False, (255, 255, 255))
                    screen.blit(axis_text_real, (WIDTH * 0.2, 20))
                    screen.blit(max_text_real, (WIDTH * 0.2, 45))
                    screen.blit(escape_real, (WIDTH * 0.2, 70))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (
                                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                                event.type == pygame.KEYDOWN and event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL):
                            pygame.quit()
                            exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RIGHT:
                                OP_AXIS = ((OP_AXIS + 1) % len(axis_key))
                                optimization_context["OP_AXIS"] = OP_AXIS
                            if event.key == pygame.K_LEFT:
                                OP_AXIS = ((OP_AXIS - 1) % len(axis_key))
                                optimization_context["OP_AXIS"] = OP_AXIS
                            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                                OP_AXIS_MAX = not OP_AXIS_MAX
                                optimization_context["OP_AXIS_MAX"] = OP_AXIS_MAX
                            if event.key == pygame.K_o or event.key == pygame.K_RETURN:
                                in_menu = False
                                break
                    pygame.display.update()
                    clock.tick(FPS)


if __name__ == '__main__':
    context, overlay_toggles, drawing_context, optimization_context = initialize()
    # drawing context
    clock = drawing_context['clock']
    FPS = drawing_context['FPS']

    # GAME LOOP
    while True:
        # user input
        check_events(context, overlay_toggles, drawing_context, optimization_context)
        # draw outfit
        display(context, drawing_context)
        # draw overlays
        draw_overlay(context, overlay_toggles, drawing_context)

        pygame.display.update()
        clock.tick(FPS)
