# LinkerScope

## Project summary

---

LinkerScope is a memory map diagram generator. It can feed itself either from a GNU Linker map file or from a custom `yaml` file
and generate beautiful and detailed diagrams of the different areas and sections found at the map files.

## Installing LinkerScope

---

Optionally create and activate an environment for LinkerScope:

```bash
python3 -m venv venv
source env/bin/activate
```

Install the needed requirements by executing:

```bash
pip3 install -r requirements.txt
```

## Usage

---

### Execution

LinkerScope is executed by running

```bash
./linkerscope.py -i linker.map -o map.svg -c config.yaml
```

where:
- `-i` specifies the path to the input file, where LinkerScope should get the data to represent from. It can come from a GNU Linker map file `.map` or from an already parsed or hand-crafted `.yaml` file. Check [Manually crafting input file](#Manually crafting input file) section for learning how to do this.
- `-o` specifies the path to the output file, which will be a newly generated SVG.
- `-c` [OPTIONAL] specifies the path to the configuration file. This file contains all the custom information to tell LinkerScope what to and how to draw the memory maps. While it is optional, the default parameters will most likely not apply to a given use case.

### Manually crafting input file
TODO

### Creating a configuration file

The configuration file is a `.yaml` file containing all the required information to tell LinkerScope what and how to draw the maps.
All information there is optional.

Normally, a configuration file contains style information, memory areas, and links.

```yaml
style:
  ...

areas:
- area:
    style:
      ...
    
    address:
      lowest: 0x0
      highest: 0x200000000
      
    size:
      ...
- area:
    ...

links:
  addresses: [ 0x80045d4, ...]
  sections: [__malloc_av_, ...]


```
#### Styles

The style can be defined at map level, where it will be applied to all areas, but also at area or even at section level.
Specifying a style at are level will override the specified configuration for the whole map where it was defined.
Specifying it at section level, it will override style information from map and area. 

```yaml
style:
  # RGB colors or english plain text color names can be used
  box_fill_color: '#CCE5FF' 
  label_color: 'blue'
  box_stroke_color: '#3399FF'
  box_stroke_width: 2
  link_stroke_width: 2
  link_stroke_color: 'grey'
  label_font: 'Helvetica Bold'
  label_size: '16px'
  label_stroke_width: 0.5px
  area_fill_color: 'lightgrey'
```
- Window:
  - `background_color`
- Map background
  - `map_background_color`
- Memory section rectangle
  - `box_fill_color`
  - `box_stroke_color`
  - `box_stroke_width`
- Section name, address and size
  - `label_color`
  - `label_font`
  - `label_size`
  - `label_stroke_width`
- Link lines between addresses at different maps
  - `link_stroke_width`
  - `link_stroke_color`

If the style at specific sections needs to be defined/overriden, it will be specified under `style -> overrides -> sections` property at
area level, by specifying the names of the regions whose properties wants to be overriden, followed by the properties to override:

```yaml
- area:
    ...
    address:
      ...
    style:
      # Area style definition
      link_stroke_color: 'grey'
      link_stroke_width: 1
      section_stroke_width: 0
      section_fill_color: 'blue'
      # Area style overrides for specified sections
      overrrides:
        - sections: [ ROM Table, Peripheral, External RAM ]
          section_fill_color: '#99B898'
        - sections: [ External PPB ]
          section_fill_color: '#FECEA8'
```
#### Areas

The diagram can have one or multiple areas. When multiple areas are declared,
first area has a special status since all links will start on it and go to the corresponding sections on the other areas
The following characteristics of a map can be defined
- `x` and `y`: absolute position 
- `size_x` and `size_y`: absolute size
- `address`: range of addresses that must be included in the area
    - `min`: minimum address to include
    - `max`: maximum address to include
- `start`: force area to start in to a given address
- `end`: force area to end in to a given address.
- `size`: size range for the sections to show
  - `max`: maximum size of a memory section to be shown
  - `min`: minimum size of a memory section to be shown
- `style`: custom style for the given area, according to [Styles](####Styles) section.

#### Links

A link between same sections or addresses drawn at different areas can be created for making, for instance, _zoom_ in effects.
For creating links between addresses, add the address value within a list under the `addresses` key.
Do the same for creating links between sections.
When specifying a section, both links for start and end of the section will be drawn. 
If any area doesn't have one of the listed addresses or sections, the link will not be drawn for that section.

```yaml
links:
  addresses: [ 0x80045d4, 0x20000910, 0x200004e8]
  sections: [HAL_RCC_OscConfig, __malloc_av_]
```

## Run some examples LinkerScope

---

At the folder examples, there are a series of configurations and map `.yaml` files you can use to get a preview of what LinkerScope can do.

## License

---

Distributed under the MIT License. See `LICENSE` for more information.
