# Setup instructions

## Non-docker

### Prerequisites

Install all required packages. It is recommended to use a virtual environment.

``` bash
pip install -r requirements.txt
```

### Create migrations and run the server

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

## Docker

Follow the instructions on the [README](README.md). On the command line do:

``` bash
docker compose -f docker-compose.yml build --no-cache
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml exec web python manage.py migrate
docker compose -f docker-compose.yml exec web python manage.py createsuperuser
```

Navigate to the web address to start.

## Starting the application (first use)

Once you start the server (either through Docker or a traditional installation), if you navigate to the address you will be directed to the dashboard login:

![](setup-images/figure1.png)

Login using the "super user" you created. Once you login, you will be directed to the dashboard:

![](setup-images/figure2.png)

On the web address, remove `dashboard` and write `admin` instead. This will direct you to the administration page.

![](setup-images/figure3.png)

The first thing you should configure is the **`Users`** menu. Click on it, and you will see the following page:

![](setup-images/figure4.png)

On the repository, there is a folder called `examples`, which we will use to do the first setup. Those are mock data, just to enable you to understand the functioning of the platform.

Click on import, and on the `examples` folder select the file `users.csv`. It has the following structure:

|username |first_name |last_name |email              |is_staff |
|:--------|:----------|:---------|:------------------|:--------|
|user_1   |Name A     |Surname A |user_1@example.com |FALSE    |
|user_2   |Name B     |Surname B |user_2@example.com |FALSE    |

![](setup-images/figure5.png)

Once you import it, the added users will be shown on the Users page:

![](setup-images/figure6.png)

Note that you need to **manually edit the password**. Because of encryption it is not possible to upload it through the "Import" function. Click on the user you want to edit, and then click on "Set password":

![](setup-images/figure7.png)

Type the new password and save. By default, the user will need to make a new password on the first access (although you can change this on the "User access" menu).

![](setup-images/figure8.png)

Once this step is completed, we can populate the remaining sections. We will need to do in the following order:

1. `Species groups`
2. `Users access`
3. `Species`
4. `Assigned species`

> [!IMPORTANT]
> You should populate the fields on this order because there is dependency between the categories. For example, the `User access` provide access to users to specific groups (from `Species groups`). If you import `User access` first, then you will need to later add the groups access for each user manually.

On the `Species groups`, import the `groups.csv`, which has this simple structure (name of the groups, in this case, families):

|name     |
|:--------|
|Family 1 |
|Family 2 |

![](setup-images/figure9.png)

On the `User access`, import the `access.csv`:

| id|user_code |groups |
|--:|:---------|:------|
|  1|user_1    |1,2    |
|  2|user_2    |1      |

You see that the groups are coded as numbers for the import - those are the "IDs" of the groups you previously imported (the row numbers, so first group = 1, second group = 2, and so on). You can also leave this column blank, click on each user and then add the groups manually.

![](setup-images/figure10.png)

In this same menu you can also see which users accepted the consent message and changed their password. If you dont' want them to change password and the consent is not needed, just change this field for each user.

Next we will import the `Species`, using the `species.csv` file:

|    key|name      |group    |
|------:|:---------|:--------|
| 422490|Species 1 |Family 1 |
| 124249|Species 2 |Family 1 |

![](setup-images/figure11.png)

> [!IMPORTANT]
> You need to unzip the file `species.zip` on `examples` and transfer its content to `review/static/review/species`. This is the data that will be shown to users when they access the dashboard. **See next section to understand where the species data (maps, etc) is located and how you can change it (for example, to access directly from an S3 bucket).** 

And finally we will populate the `Assigned species`, using the `assigned.csv` file:

|user_code | species_key|
|:---------|-----------:|
|user_1    |      107276|
|user_1    |      422490|

That is, for each user, multiple `species_key` (which is the same as the `Species` section `key` field) can be added.

![](setup-images/figure12.png)

The final step is to add the questions. Go to `Questions` and add it manually (it is not possible to import). You can use the questions provided on `examples/questions.md`. You can add multiple choice and free text questions, as well as "select on the map" questions, which return WKT responses.

![](setup-images/figure13.png)

![](setup-images/figure14.png)

Once this is done, you can logout and login again as a user (use for example user_1 and the password you set). Once you login, you will see the "Change the password" page:

![](setup-images/figure15.png)

![](setup-images/figure16.png)

Completing this step will redirect you to the evaluation page for the first species on the list:

![](setup-images/figure17.png)

If you click on the `Dashboard` link on the corner, you can then see all the species that should be evaluated:

![](setup-images/figure18.png)

When you complete the evaluations you will either see a screen showing that all species were evaluated:

![](setup-images/figure19.png)

Or be invited to evaluate more species (if there are more on the families the user has access):

![](setup-images/figure20.png)

Returning to the dashboard will also show the option to evaluate more species (if there are any available):

![](setup-images/figure21.png)

Now logout and go back to the admin page. You can see three options on the top: "View Dashboard", "View Evaluations" and "Download data and code".

![](setup-images/figure22.png)

By clicking on "View Dashboard" you can have an overview of all the responses:

![](setup-images/figure23.png)

"View Evaluations" will redirect you to the "Evaluations" page:

![](setup-images/figure24.png)

There you can export the responses in many formats:

![](setup-images/figure25.png)

The option "Download data and code" will download a zipped folder containing the data for each field, the evaluations and an R script to run analyses on the data.

![](setup-images/figure26.png)


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

To clean up the project, remove the SQLite database (`db.sqlite3`). Then run the previous steps.

Note: this will remove any data you have previously imported, and it will also delete any user that was created.

## Changing the project logo and help page

The project logo is on `review/static/review/img/logo.png`.

The help page is buil using images on `review/static/review/img/help`. You can then alter the text on `review/templates/help.html`