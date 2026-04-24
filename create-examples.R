fs::dir_create("examples")

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
        key = c(1001, 1002, 1003, 1004, 1005),
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
    write.csv(df, "examples/access.csv", row.names=  FALSE)
}

generate_access()

generate_assigned <- function() {
    df <- data.frame(
        user_code = c(rep("user_1", 2), rep("user_2", 3), paste0("user_", 3:5)),
        species_key = sample(c(1001, 1002, 1003, 1004, 1005), 8, replace = T)
    )
    write.csv(df, "examples/assigned.csv", row.names=  FALSE)
}

generate_assigned()
