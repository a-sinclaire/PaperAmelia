import pygame
import pandas as pd
import os
import random
from copy import deepcopy


def scale_img(img, scale):
    return pygame.transform.scale(img, (img.get_width() / scale, img.get_height() / scale))


def initialize():
    # read in csv of clothes data and store in pandas dataframe
    df = pd.read_csv('../Assets/directory.csv')
    # read in layer info csv and store in pandas dataframe
    layer_info_df = pd.read_csv('../Assets/layer_info.csv')

    # setting scale
    SCALE = 4.0
    # loading background image
    BACKGROUND_IMG = pygame.image.load('../Assets/BACKGROUND.png')
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
    DISPLAY_GUI = True
    LOAD_DEFAULT = True
    SHOW_HELP = False
    SHOW_STATS = False
    axis_key = ['total_coverage', 'weight', 'avg_thickness', 'avg_breathability', 'waterproof', 'avg_brightness',
                'sportiness', 'formality', 'loungeablity', 'warmth']
    OP_AXIS = 7
    OP_AXIS_MAX = True

    # getting some info
    num_layers = layer_info_df.shape[0]
    current_layer = 1
    min_layer = 1
    max_layer = num_layers - 1
    item_index = [0] * num_layers

    num_items = [0] * num_layers
    for layer in range(num_layers):
        num_items[layer] = len(df[df.layer == layer])

    status = [None] * num_layers
    for layer in range(num_layers):
        for x in range(len(num_items)):
            status[layer] = [False] * num_items[layer]
    status[0][0] = True

    locked = [False] * num_layers

    if LOAD_DEFAULT:
        default_df = pd.read_csv('../Assets/default.csv')
        for index, row, in default_df.iterrows():
            status[row['layer']][row['item_index']] = True
            item_index[row['layer']] = row['item_index']

    sprites = [None] * df.shape[0]
    # append column for sprites to the clothes dataframe
    df = df.assign(Sprite=sprites)

    context = (df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked)
    return context


def shuffle(context, outfit_status=None):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    working_status = status
    if outfit_status is not None:
        working_status = outfit_status
    # randomize
    for l in range(num_layers):
        if locked[l]:
            continue
        if l == 0:
            continue
        copy = working_status[l]
        for x in range(len(copy)):
            copy[x] = False
        working_status[l] = copy

        r = random.randrange(0, num_items[l])
        if random.randrange(0, num_items[l] * 10) <= 5:
            continue
        working_status[l][r] = True
    return working_status.copy()


def minor_shuffle(context, z, k, s=None):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    if locked[z]:
        return
    # choose a random layer to shuffle
    # z = random.randrange(1, num_layers)
    status_copy = deepcopy(status)
    if s is not None:
        status_copy = s

    # turn off all items in that layer
    copy = status_copy[z]
    for x in range(len(copy)):
        copy[x] = False
    status_copy[z] = copy

    # random chance to just exit (removing all items in this layer)
    # if random.randrange(0, num_items[z]+2) <= 1:
    if k > num_items[z] - 1:
        return status_copy

    # choose a random item to turn on
    # r = random.randrange(0, num_items[z])
    status_copy[z][k] = True
    return status_copy


def major_optimize(context, axis, max_iterations, max=True):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 20, 20), 10)
    pygame.display.update()

    # get score for current outfit / set it to max score / save current outfit
    stats = calc_stats(context)
    max_score = stats[axis]

    save_outfit = deepcopy(status)
    for i in range(max_iterations):
        # get new random outfit / score it
        new_outfit = shuffle(context, deepcopy(status))
        stats = calc_stats(context, new_outfit)
        new_score = stats[axis]
        # if new score is better, new score is new max score / save this outfit as current best
        if max:
            if new_score > max_score:
                max_score = new_score
                save_outfit = deepcopy(new_outfit)
                status = deepcopy(save_outfit)
                context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
                display(context)
                draw_overlay(context)
                pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 20, 20), 10)
                pygame.display.update()
                break
        else:
            if new_score < max_score:
                max_score = new_score
                save_outfit = deepcopy(new_outfit)
                status = deepcopy(save_outfit)
                context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
                display(context)
                draw_overlay(context)
                pygame.draw.circle(screen, (255, 0, 0), (WIDTH - 20, 20), 10)
                pygame.display.update()
                break
    # assign the best found outfit to be current status
    status = deepcopy(save_outfit)
    # update current item index
    for l in range(len(status)):
        for a in range(len(status[l])):
            if status[l][a]:
                item_index[l] = a
    context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
    return context


def multi_opt(context, axis_array, iterations):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
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
        context = minor_optimize(context, index_array[ind[0]], 1, axis_array_maxs[ind[0]], rand=True)
    return context


def minor_optimize(context, axis, iterations, max=True, rand=False):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
    pygame.display.update()

    # get score for current outfit / set it to max score / save current outfit
    stats = calc_stats(context)
    max_score = stats[axis]

    similarity_counter = 0

    # original outfit stored in save_outfit
    save_outfit = deepcopy(status)
    for i in range(iterations):
        # find minor improvements randomly
        # operate on 'next layer', try next article of clothing
        layer_op = (i % (max_layer)) + 1
        if rand:
            r = random.randrange(0, max_layer)
            layer_op = ((i+r) % (max_layer)) + 1
        item_op_offset = random.randrange(0, num_items[layer_op] + 1)
        for j in range(num_items[layer_op] + 1):
            item_op = ((j+item_op_offset) % (num_items[layer_op] + 1))
            # if rand:
            #     r = random.randrange(0, num_items[layer_op] + 1)
            #     item_op = ((j+r) % (num_items[layer_op] + 1))
            new_outfit = minor_shuffle(context, layer_op, item_op, deepcopy(status))
            #
            # display(new_outfit)
            # draw_overlay()
            # pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
            # pygame.display.update()
            #
            stats = calc_stats(context, new_outfit)
            new_score = stats[axis]
            # if new score is better, new score is new max score / save this outfit as current best
            if max:
                if new_score > max_score:
                    max_score = new_score
                    save_outfit = deepcopy(new_outfit)
                    status = deepcopy(new_outfit)
                    context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
                    display(context)
                    draw_overlay(context)
                    pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
                    pygame.display.update()
            else:
                if new_score < max_score:
                    max_score = new_score
                    save_outfit = deepcopy(new_outfit)
                    status = deepcopy(new_outfit)
                    context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
                    display(context)
                    draw_overlay(context)
                    pygame.draw.circle(screen, (0, 0, 255), (WIDTH - 20, 40), 10)
                    pygame.display.update()
        if status == save_outfit:
            similarity_counter += 1
        else:
            similarity_counter = 0
        if similarity_counter >= num_layers * 3:
            # print("CONVERGED!")
            for l in range(len(status)):
                for a in range(len(status[l])):
                    if status[l][a]:
                        item_index[l] = a
            context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
            return context
    # assign the best found outfit to be current status
    status = deepcopy(save_outfit)
    for l in range(len(status)):
        for a in range(len(status[l])):
            if status[l][a]:
                item_index[l] = a
    context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
    return context


def map_range(input, in_min, in_max, out_min, out_max):
    slope = (out_max - out_min) / (in_max - in_min)
    return out_min + slope * (input - in_min)


def calc_stats(context, outfit_status=None):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    working_status = status
    if outfit_status is not None:
        working_status = outfit_status
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
        for i in range(len(working_status[l])):
            if working_status[l][i]:
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
    if num_layers != 0 and n_clothes != 0:
        avg_thickness = (avg_thickness / (num_layers - 1)) * 100.00
        avg_breathability = 100.00 - ((avg_breathability / (num_layers-1)) * 100.00)
        # avg_waterproofing = (avg_waterproofing / (num_layers-1)) * 100.00
        # avg_brightness = (avg_brightness / (num_layers-1)) * 100.00
        sportiness = (sportiness / (num_layers-1)) * 100.00
        formality = (formality / (num_layers-1)) * 100.00
        loungeablity = (loungeablity / (num_layers-1)) * 100.00

        avg_waterproofing = (100.00 * avg_waterproofing) / total_coverage
        avg_brightness = (100.00 * avg_brightness) / total_coverage
        warmth = (100.00 * warmth) / total_coverage
    # avg_brightness *= 100.00
    # sportiness *= 100.00
    # formality *= 100.00
    # loungeablity *= 100.0
    return (
    total_coverage, weight, avg_thickness, avg_breathability, avg_waterproofing, avg_brightness, sportiness, formality,
    loungeablity, warmth)


def display(context, outfit_status=None):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    working_status = status
    if outfit_status is not None:
        working_status = outfit_status
    screen.blit(BACKGROUND_IMG, (0, 0))  # draw BG

    if DISPLAY_GUI:
        layer_name = layer_info_df.iloc[current_layer]['name']
        if locked[current_layer]:
            layer_name += ' (L)'
        layer_info = my_font.render('<-layer->: ' + layer_name, False, (255, 255, 255))
        screen.blit(layer_info, (20, 20))
        item_info = my_font.render('^itemv: ' + str(item_index[current_layer]), False, (255, 255, 255))
        screen.blit(item_info, (20, 50))
        if num_items[current_layer] != 0:
            item_info_on = my_font.render('status: ' + str(working_status[current_layer][item_index[current_layer]]),
                                          False,
                                          (255, 255, 255))
            screen.blit(item_info_on, (20, 80))

    # display character
    for layer in range(num_layers):
        if num_items[layer] == 0:
            continue
        # if the layer we are currently processing is not the layer we are editing
        # and if all items in this layer are off skip
        # if layer != current_layer and not status[layer][item_index[layer]]:
        #     continue
        items_in_layer = df[df.layer == layer]  # all items in this layer

        # draw all items that are TURNED ON (in the process layer)
        for i in range(len(working_status[layer])):
            if working_status[layer][i]:
                row = items_in_layer.iloc[i]
                # load in img if need be
                if row['Sprite'] is None:
                    print('Loading img: ', row['img_name'], ' ...')
                    s = pygame.image.load('../Assets/' + str(row['img_name']))
                    s = scale_img(s, SCALE)
                    row['Sprite'] = s
                    # add the sprite to the actual dataframe
                    real_row_index = df.index[df['img_name'] == row['img_name']].tolist()[0]
                    df.at[real_row_index, 'Sprite'] = s
                screen.blit(row['Sprite'], (row['x'], row['y']))

    # draw preview image of current item
    if DISPLAY_GUI and num_items[current_layer] != 0:
        items_in_layer = df[df.layer == current_layer]  # all items in this layer
        cur_item_index = [item_index[current_layer]]
        row = items_in_layer.iloc[cur_item_index]
        # load in img if need be
        if row['Sprite'].values[0] is None:
            print('*Loading img: ', row['img_name'].values[0], ' ...')
            s = pygame.image.load('../Assets/' + str(row['img_name'].values[0]))
            s = scale_img(s, SCALE)
            row['Sprite'] = s
            # add the sprite to the actual dataframe
            real_row_index = df.index[df['img_name'] == row['img_name'].values[0]].tolist()[0]
            df.at[real_row_index, 'Sprite'] = s
        screen.blit(row['Sprite'].values[0], (row['x'].values[0] - (WIDTH * 0.3), row['y'].values[0]))


def draw_overlay(context):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
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


def check_events(context):
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL):
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                DISPLAY_GUI = not DISPLAY_GUI
            if event.key == pygame.K_LEFT and DISPLAY_GUI:
                current_layer = current_layer - 1
                if current_layer < min_layer:
                    current_layer = min_layer
            if event.key == pygame.K_RIGHT and DISPLAY_GUI:
                current_layer = current_layer + 1
                if current_layer > max_layer:
                    current_layer = max_layer
            if event.key == pygame.K_UP and DISPLAY_GUI:
                if num_items[current_layer] == 0:
                    break
                item_index[current_layer] += 1
                item_index[current_layer] = item_index[current_layer] % num_items[current_layer]
            if event.key == pygame.K_DOWN and DISPLAY_GUI:
                if num_items[current_layer] == 0:
                    break
                item_index[current_layer] -= 1
                item_index[current_layer] = item_index[current_layer] % num_items[current_layer]
            if event.key == pygame.K_RETURN and DISPLAY_GUI:
                status[current_layer][item_index[current_layer]] = not status[current_layer][item_index[current_layer]]
            if event.key == pygame.K_x:
                copy = status[current_layer]
                for x in range(len(copy)):
                    copy[x] = False
                status[current_layer] = copy
            if event.key == pygame.K_x and pygame.key.get_mods() & pygame.KMOD_CTRL:
                for l in range(num_layers):
                    if l == 0:
                        continue
                    copy = status[l]
                    for x in range(len(copy)):
                        copy[x] = False
                    status[l] = copy
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                print("SCREENSHOT")
                dir_path = '../Screenshots'
                count = 0
                for path in os.listdir(dir_path):
                    if os.path.isfile(os.path.join(dir_path, path)):
                        count += 1
                while os.path.exists("../Screenshots/screenshot" + str(count) + ".png"):
                    count += 1
                pygame.image.save(screen, str("../Screenshots/screenshot" + str(count) + ".png"))
            if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # load all unloaded assets
                for i in range(num_layers):
                    items_in_layer = df[df.layer == i]  # all items in this layer
                    for j in range(num_items[i]):
                        row = items_in_layer.iloc[j]
                        # load in img if need be
                        if row['Sprite'] is None:
                            print('Loading img: ', row['img_name'], ' ...')
                            s = pygame.image.load('../Assets/' + str(row['img_name']))
                            s = scale_img(s, SCALE)
                            row['Sprite'] = s
                            # add the sprite to the actual dataframe
                            real_row_index = df.index[df['img_name'] == row['img_name']].tolist()[0]
                            df.at[real_row_index, 'Sprite'] = s
            if event.key == pygame.K_y:
                status[0][0] = not status[0][0]
            if event.key == pygame.K_h:
                SHOW_HELP = not SHOW_HELP
            if event.key == pygame.K_t:
                SHOW_STATS = not SHOW_STATS
            if event.key == pygame.K_r:
                status = shuffle(context)
                context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
                for l in range(len(status)):
                    for a in range(len(status[l])):
                        if status[l][a]:
                            item_index[l] = a
            if event.key == pygame.K_m:
                context = major_optimize(context, OP_AXIS, 1000, OP_AXIS_MAX)
                df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
            if event.key == pygame.K_n:
                context = minor_optimize(context, OP_AXIS, 300, OP_AXIS_MAX)
                df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
                # multi_opt(None, 100)
            if event.key == pygame.K_l:
                # lock current layer
                locked[current_layer] = True
            if event.key == pygame.K_u:
                # unlock current layer
                locked[current_layer] = False
            if event.key == pygame.K_o:
                # save menu states
                save_gui = DISPLAY_GUI
                save_help = SHOW_HELP
                save_stats = SHOW_STATS
                # turn off menus
                DISPLAY_GUI = False
                SHOW_HELP = False
                SHOW_STATS = False
                context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
                # optimize menu popup
                in_menu = True
                while in_menu:
                    display(context)
                    draw_overlay(context)
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
                            if event.key == pygame.K_LEFT:
                                OP_AXIS = ((OP_AXIS - 1) % len(axis_key))
                            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                                OP_AXIS_MAX = not OP_AXIS_MAX
                            if event.key == pygame.K_o or event.key == pygame.K_RETURN:
                                in_menu = False
                                break
                    pygame.display.update()
                    clock.tick(FPS)
                DISPLAY_GUI = save_gui
                SHOW_HELP = save_help
                SHOW_STATS = save_stats
    context = df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked
    return context


if __name__ == '__main__':
    context = initialize()
    df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
    while True:
        # user input
        context = check_events(context)
        df, layer_info_df, SCALE, FPS, BACKGROUND_IMG, WIDTH, HEIGHT, screen, clock, my_font, DISPLAY_GUI, SHOW_HELP, SHOW_STATS, axis_key, OP_AXIS, OP_AXIS_MAX, num_layers, current_layer, min_layer, max_layer, item_index, num_items, status, locked = context
        display(context)
        draw_overlay(context)

        pygame.display.update()
        clock.tick(FPS)