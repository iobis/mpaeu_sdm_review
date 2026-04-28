# Setup instructions

## Prerequisites

Install all required packages. It is recommended to use a virtual environment.

``` bash
pip install -r requirements.txt
```

## Create migrations and run the server

From the project root folder, run the following commands to create the database tables and apply migrations:

``` bash
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations review
python manage.py migrate review
```

Now you can run the development server again:

``` bash
python manage.py runserver
```

You will need to create a superuser account. To create a superuser, run:

``` bash
python manage.py createsuperuser
```

## Starting the application (first use)

Once you start the server (either through Docker or a traditional installation), if you navigate to the address you will be directed to the dashboard login:

First `Species Groups`, `Access` and then `Species` and then `Assigned`





## Changing species information structure

By default, the species information is displayed across 6 tabs:

- Species information: show basic species information
- Suitability: show suitability maps
- Suitability - core area: show suitability maps for core area only (thresholded)
- Sampling locations: occurrence records used to fit the model
- Alternative models: other predictions
- Future predictions: predictions for future periods

Species data can be stored locally (e.g. `review/static/review/species/`) or in an external source (for example an S3 bucket). To alter the source from the files, edit the `base_url` at `views.py`. File names follows the standard taxonid={species_id}_{data_type}.{extension}. For example, for species with taxonid 107276, we have the following files:

- taxonid=107276_current.tif [suitability map]
- taxonid=107276_current_th.tif [suitability map thresholded]
- taxonid=107276_pts.csv [occurrence records]
- taxonid=107276_others.png [plot of other models predictions]
- taxonid=107276_current_th_ssp1.tif [future prediction]
- taxonid=107276_current_th_ssp3.tif [future prediction]

You can also modify this structure by changing the templates and the views.

### Modifying templates

Three templates are involved in displaying species information:

- review/templates/evaluate.html: main template for the species evaluation page
- review/templates/species_info.html: template for the species information tab
- review/templates/map.html: template for maps (works as a function)

**Modifying evaluate.html**

The `evaluate.html` contains the structure of the evaluation page. It basically consists of three parts: tabs navigation, tab content, and the questions form. In this part you can modify the tabs structure, adding or removing tabs as needed.

For each tab, you should have a component like this in the navigation section:

```html
<li class="nav-item" role="presentation">
    <button class="nav-link active" id="tab-one-tab" data-bs-toggle="tab" data-bs-target="#tab-one" type="button"
        role="tab" aria-controls="tab-one" aria-selected="true">
        Species information
    </button>
</li>
```

With the corresponding content section like this:

```html
<div class="tab-pane fade show active" id="tab-one" role="tabpanel" aria-labelledby="tab-one-tab">
    <!-- Each tab can have a different content; here we are including content from another html file -->
    {% include "species_info.html" %}
</div>
```

For the dynamic fields, this page uses content produced by the functions of `views.py`. For example, the function `evaluate_next_species` produces the following context for this template:

```python
context = {
    'species': current_species,
    'questions': questions,
    'error': error, 
    'current': f"{base_url}taxonid={species_key}_current.tif",
    'current_th': f"{base_url}taxonid={species_key}_current_th.tif",
    'points': f"{base_url}taxonid={species_key}_pts.csv",
    'future': f"{base_url}taxonid={species_key}_current_th_ssp1.tif",
    'future_b': f"{base_url}taxonid={species_key}_current_th_ssp3.tif",
    'others': f"{base_url}taxonid={species_key}_others.png",
    'json_url': f"{base_url}taxonid={species_key}_log.json",
}
```

**Modifying species_info.html**

The `species_info.html` contains the content of the species information tab. It fetches a JSON file with all modelling details ((see more here)[https://iobis.github.io/mpaeu_docs/datause.html#understanding-the-log-file]) and also retrieves basic species information through the OBIS and WoRMS API.

**Modifying map.html**

The `map.html` is a reusable component for displaying maps through leaflet.js. In general you don't need to modify this template, unless you want to change the map appearance (for example, colors).

## Cleanup instructions

To clean up the project, remove the SQLite database (`db.sqlite3`) and delete all migrations (remove folder `migrations`). Then run the previous steps.

Note: this will remove any data you have previously imported, and it will also delete any user that was created.

## Changing the project logo and help page

The project logo is on `review/static/review/img/logo.png`.

The help page is buil using images on `review/static/review/img/help`. You can then alter the text on `review/templates/help.html`