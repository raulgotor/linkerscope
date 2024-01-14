# LinkerScope

## Project summary

LinkerScope is a memory map diagram generator. It can feed itself either from a GNU Linker map file or from a custom `yaml` file
and generate beautiful and detailed diagrams of the different areas and sections found at the map files.

## Installing LinkerScope

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

### Execution

LinkerScope is executed by running

```bash
./linkerscope.py -i linker.map -o map.svg -c config.yaml
```

where:
- `-i` specifies the path to the input file, where LinkerScope should get the data to represent from. It can come from a GNU Linker map file `.map` or from an already parsed or hand-crafted `.yaml` file. Check [Manually crafting input file](#Manually crafting input file) section for learning how to do this.
- `-o` specifies the path to the output file, which will be a newly generated SVG.
- `-c` [OPTIONAL] specifies the path to the configuration file. This file contains all the custom information to tell LinkerScope what to and how to draw the memory maps. While it is optional, the default parameters will most likely not apply to a given use case.

### Input files

#### Manually crafted memory map files

Linkerscope can use two types of input files: GNU linker map files (`.map`) or custom defined yaml files (`.yaml`).

Custom memory map files can be manually crafted and can run from a couple of memory sections up to very complex memory schemes with hundreds of sections.
Normally you would do that when representing simple memory maps.

For making a memory map file, one has to specify at least a single section. Each section must include
an `id`, an `address` and a `size`.

While these three are needed, there are other possible attributes that are optional:

- `name`: Friendly text name that would be used instead of the `id`
- `type`: Section type, which can be used for different purposes. Possibilities are `section` (default) and `area`.

The input file should contain the `map` keyword whose value is an array of sections. Below an example
of how an input file should look like:

```yaml
- address: 0x80045D4
  size:    0x0000F00
  id:      .rodata
  name:    Read Only Data
  type:    area
- address: 0x8002C3C
  id:      SysTick_Handler
  size:    0x0000008
- ...
```

In order to use this file, invoke Linkerscope and specify the yaml map file as input:

```bash
./linkerscope.py -i memory_map.yaml -o memory_map.svg -c config.yaml
```

#### Automatically generated memory map files

For a complex diagram that fully represents the memory map of a given program, handcrafting the memory map can be
time-consuming. In the case that the intended diagram is related to a program, the necessary information is already
available at the generated GNU Linker map files.
Linkerscope conveniently provides the possibility to parse these files and generate diagram from those. For that, simply
specify the `.map` file as an input.

```bash
./linkerscope.py -i linker.map -o map.svg -c config.yaml
```

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
- Area background
  - `area_background_color`
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

If the style at specific sections needs to be defined/overridden, it will be specified under `style -> overrides -> sections` property at
area level, by specifying the names of the regions whose properties want to be overridden, followed by the properties to override:

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
The areas are declared at root level under `areas`. Then each area must use the key `area`.
For each area, the following characteristics of an area can be defined:
- `title`:  **[Optional, none]**
  - The title of the area, which will appear on top of it
- `pos`:  **[Optional, (50, 50)]** **[x, y]**
  - absolute position  of the area's top-left corner in pixels
- `size`:  **[Optional, (300, 600)]** **[width, height]**
  - area size in pixels
- `range`:  **[Optional, (0, no limit)]** **[min, max]**
  - range of addresses that will be taken into account in this area.
# - `start`: **[start, end]** force area to start in to a given address
- `section-size`: **[Optional, (0, no limit)]** **[min, max]**
  - size range of the sections that should be shown. Exclude others.
- `style`:  **[Optional, default: parent style]**
  - specific style for current area. See [Styles](####Styles) section.
- `sections`: **[Optional, none]**
  - specify or modify a section or group of sections property such as `style`, `flags`,...
    - `names`:
      - list of one or more sections to modify with the parameters below
    - `flags`: **[Optional, none]**
      - flags to append to the specified section/s. See [Flags](#### Section flags) section.
    - `style`: **[Optional, parent style]**
      - style properties to or modify to the specified section/s
- `labels`: **[Optional, none]**
  - Add text labels to specific memory positions of the current area
    - `address`:
      - Memory address where the label should be placed
    - `text`:
      - Text to display for this label
    - `lenght`: **[Optional, none]**
      - lenght of the label line in pixels
    - `directions`: **[Optional, none]**
      - direction or list of directions for the arrow head. Possible values are none, `in`, `out` or both.
    - `side`: **[Optional, `right`]**
      - Area side at which the label should be placed
    - `style`: **[Optional, parent style]**
      - style properties to or modify to the specified section/s

Below an example of area definition:

```yaml
areas:
- area:
    title: 'Full Memory Map'
    pos: [30, 50]
    size: [300, 900]
    range: [0x0, 0x100000000]
    section-size: [0x02F00000]
    style:
      fill: *pastel_green
    sections:
    - names: [ External Device ]
      flags: grows-up
      style:
        hide-size: true
```
#### Labels

Labels can bind a text string with a specific memory position. This property falls inside `area`. A partial example can
be seen below:

```yaml
areas:
 - area:
    labels:
      - address: 0xe8043800
        text: In direction
        length: 150
        directions: in
        style:
          stroke-dasharray: '5,1,3,1,3'
     # ...
```

<img style="display: block; margin-left: auto; margin-right: auto;" src="examples/label_example_map.svg">

> See `examples/label_example_config.yaml` for a full example.

#### Section flags

Section flags allows to flag specified sections with special properties. These properties are listed below:

Flags are listed under property `flags` and can be specified both at the map files under each section

```yaml
# flags can be defined at map.yaml files under each section
map:
- address: 0x20000000
  id: stack
  # ...
  flags: grows-down, break
```

or at the configuration files, with the possibility to specify multiple sections at the same time:

```yaml
# flags can be defined at config.yaml files under each section or group of sections
areas:
- area:
  # ...
  sections:
  - names: [ROM Table, TPIU]
    flags: break
```

##### `grows-up` / `grows-down`
These flags specify the section as growing section, for instance, if the section is meant to grow into one direction, such as the stack.
When flagging a section with `grows-down`, an arrow pointing downwards will be appended to the bottom of the section indicating that the section is growing into that direction:

<img style="display: block; margin-left: auto; margin-right: auto;" src="examples/stack_example_map.svg">

##### `break`

A break or discontinuous section shortens a sized section to a fixed size by drawing a symbol representing a discontinuity across it.
This is specially useful when wanting to include several sections of considerable different sizes in one diagram.
Reducing the size of the biggest one helps to visually simplify the diagram and evenly distribute the space.

There are four different break styles, which can be defined by the 'break-type' style property: `~`: Wave,  `≈`: Double wave, `/`: Diagonal, `...`: Dots

<img style="display: block; margin-left: auto; margin-right: auto;" src="examples/break_example_map.svg">

#### Links

Links establish a connection between same addresses or sections at different areas.

While address links are represented with a finite line between the addresses, section link drawing
cover the whole region space. These can be used,for instance, to represent a _zoom_ in effects from one overview area
to other area with more detail.

> When drawing a section link, Linkerscope expects both start and end section addresses to be visible at both intended areas.
If any of those is not present, the link will not be drawn

Links are defined at root level under the `links` tag. Links must have either `addresses` or `sections` tags or both.
Additionally, specific styles can be specified under the `style` tag.


```yaml
links:
  style:
    stroke: 'lightgray'
    stroke-width: 1
    fill: 'gray'
  addresses: [ 0xe8040000 ]
  sections: [['Bit band region', 'Bit band alias']]

```
<img style="display: block; margin-left: auto; margin-right: auto;" src="examples/link_example_map.svg">

#### Other properties

##### Document size

The generated SVG document has a fixed size. If you want to adjust it, use the `size` property at root level to pass
desired document width and height in pixels.

## Run some examples with LinkerScope

At the folder examples, there are a series of configurations and map `.yaml` files you can use to get a preview of what LinkerScope can do.

## Roadmap

- [x] Labels at specific memory addresses
- [x] Area titles
- [x] Links across specific areas
- [x] Choose side of the labels
- [x] Memory direction
- [x] Hide specific elements
- [ ] Memory size in bytes
- [ ] Section links across breaks
- [x] Friendly name and identifier
- [ ] Legend
- [ ] Area representation different from section
- [ ] Make `type` default to `section`
- [ ] Bug: title appears at top of each break section, if long enough

## References

- [YAML cheatsheet](https://quickref.me/yaml)

## License

Distributed under the MIT License. See `LICENSE` for more information.
