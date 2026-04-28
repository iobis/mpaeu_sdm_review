fs::dir_create("examples")
fs::dir_create("examples/species")
set.seed(2026)

generate_users <- function() {
    df <- data.frame(
        username = paste0("user_", 1:5),
        first_name = paste("Name", LETTERS[1:5]),
        last_name = paste("Surname", LETTERS[1:5]),
        email = paste0(paste0("user_", 1:5), "@example.com"),
        is_staff = FALSE
    )
    write.csv(df, "examples/users.csv", row.names = FALSE)
}

generate_users()

generate_sp_groups <- function() {
    df <- data.frame(
        name = c("Family 1", "Family 2")
    )
    write.csv(df, "examples/groups.csv", row.names = FALSE)
}

generate_sp_groups()

generate_species <- function() {
    df <- data.frame(
        key = c(422490, 124249, 213372, 107379, 107276),
        name = paste("Species", 1:5),
        group = c(rep("Family 1", 3), rep("Family 2", 2))
    )
    write.csv(df, "examples/species.csv", row.names = FALSE)
}

generate_species()

generate_access <- function() {
    df <- data.frame(
        id = 1:5,
        user_code = paste0("user_", 1:5),
        groups = c("1,2", "1", "1", "1,2", "2")
    )
    write.csv(df, "examples/access.csv", row.names = FALSE)
}

generate_access()

generate_assigned <- function() {
    df <- data.frame(
        user_code = c(rep("user_1", 2), rep("user_2", 3), paste0("user_", 3:5)),
        species_key = sample(c(422490, 124249, 213372, 107379, 107276), 8, replace = T)
    )
    df <- df |> dplyr::group_by(user_code) |> dplyr::distinct(species_key)
    write.csv(df, "examples/assigned.csv", row.names = FALSE)
}

generate_assigned()

download_sample <- function() {
    require(terra)

    species <- c(422490, 124249, 213372, 107379, 107276)

    for (sp in species) {
        current <- rast(
            paste0("/vsicurl/https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/predictions/taxonid=", sp, "_model=mpaeu_method=maxent_scen=current_cog.tif")
        )
        mask <- rast(
            paste0("/vsicurl/https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/predictions/taxonid=", sp, "_model=mpaeu_what=mask_cog.tif")
        )

        NAflag(mask) <- 0

        current <- mask(current, mask$fit_region_max_depth)

        writeRaster(current,
            file.path("examples/species", paste0("taxonid=", sp, "_current.tif")),
            filetype = "COG",
            overwrite = TRUE
        )

        th <- arrow::read_parquet(
            paste0("https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/metrics/taxonid=", sp, "_model=mpaeu_what=thresholds.parquet")
        )
        th <- th$max_spec_sens[th$model == "maxent"] * 100

        current[current < th] <- 0

        writeRaster(current,
            file.path("examples/species", paste0("taxonid=", sp, "_current_th.tif")),
            filetype = "COG",
            overwrite = TRUE
        )

        pts <- arrow::read_parquet(
            paste0("https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/taxonid=", sp, "_model=mpaeu_what=fitocc.parquet")
        )
        pts |> write.csv(file.path("examples/species", paste0("taxonid=", sp, "_pts.csv")), row.names = F)

        ssp1 <- rast(
            paste0("/vsicurl/https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/predictions/taxonid=", sp, "_model=mpaeu_method=maxent_scen=ssp126_dec100_cog.tif")
        ) |>
            mask(mask$fit_region_max_depth) |>
            terra::classify(matrix(c(-Inf, th, 0), nrow = 1)) |>
            writeRaster(
                file.path("examples/species", paste0("taxonid=", sp, "_current_th_ssp1.tif")),
                filetype = "COG",
                overwrite = TRUE
            )

        ssp3 <- rast(
            paste0("/vsicurl/https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/predictions/taxonid=", sp, "_model=mpaeu_method=maxent_scen=ssp370_dec100_cog.tif")
        ) |>
            mask(mask$fit_region_max_depth) |>
            terra::classify(matrix(c(-Inf, th, 0), nrow = 1)) |>
            writeRaster(
                file.path("examples/species", paste0("taxonid=", sp, "_current_th_ssp3.tif")),
                filetype = "COG",
                overwrite = TRUE
            )

        current_rf <- rast(
            paste0("/vsicurl/https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/predictions/taxonid=", sp, "_model=mpaeu_method=maxent_scen=current_cog.tif")
        ) |> mask(mask$fit_region_max_depth)

        current_xgboost <- rast(
            paste0("/vsicurl/https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/predictions/taxonid=", sp, "_model=mpaeu_method=maxent_scen=current_cog.tif")
        ) |> mask(mask$fit_region_max_depth)

        png(file.path("examples/species", paste0("taxonid=", sp, "_others.png")))
        par(mfrow = c(1, 2))
        plot(current_rf, main = "RandomForest")
        plot(current_xgboost, main = "XGBoost")
        dev.off()

        download.file(
            paste0("https://obis-maps.s3.amazonaws.com/sdm/species/taxonid=", sp, "/model=mpaeu/taxonid=", sp, "_model=mpaeu_what=log.json"),
            file.path("examples/species", paste0("taxonid=", sp, "_log.json"))
        )
    }
}

download_sample()

zip::zip("examples/species.zip", "examples/species", mode = "cherry-pick")

fs::dir_delete("examples/species")
