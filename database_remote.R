library(tidyverse)
library(ggplot2)
library(googlesheets4)

ss_name <- 'https://docs.google.com/spreadsheets/d/1F8GBPtLhugdO0pqrJe3O9fMPOYv3AqVRq8ouUZWZxIY/edit#gid=0'

# CREATE

create_database <- function(game_id, signature, pt_data_fully_tracked=FALSE, pt_data_partially_tracked=FALSE, custom_message='') {
  # Creates the database and adds the first game.
  # 
  # @description This function adds the first game to the database, and adds messages to the log saying 
  # the database has been created and the first game has been added.
  # 
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  # @param signature character. A signature for who added the game.
  # @param pt_data_fully_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is fully tracked or not.
  # @param pt_data_partially_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is partially tracked or not.
  # @param custom_message character. Optional, defaults to ''. A custom message to be added in the log message.
  # 
  # @details pt_data_fully_tracked and pt_data_partially_tracked cannot both be TRUE.
  if (!((pt_data_fully_tracked == TRUE) & (pt_data_partially_tracked == TRUE))) {
    if ((pt_data_fully_tracked == TRUE) | (pt_data_partially_tracked == TRUE)) {
      game_data_file <- paste0('~/baycats/pitches_tracked_game_data/', game_id, '_pt.csv')
    }
    else {
      game_data_file <- paste0('~/baycats/raw_game_data/', game_id, '.csv')
    }
    game_data <- read_csv(game_data_file)
    game_id <- unique(game_data$game_pk)
    
    log_db_created_message <- 'Database created.'
    if (pt_data_fully_tracked == TRUE) {
      if (custom_message != '') {
        log_message <- paste0('Game ', game_id, ' added. Pitch data fully tracked. ', custom_message)
      }
      else {
        log_message <- paste0('Game ', game_id, ' added. Pitch data fully tracked.')
      }
    }
    else if (pt_data_partially_tracked == TRUE) {
      if (custom_message != '') {
        log_message <- paste0('Game ', game_id, ' added. Pitch data partially tracked. ', custom_message)
      }
      else {
        log_message <- paste0('Game ', game_id, ' added. Pitch data partially tracked.')
      }
    }
    else {
      if (custom_message != '') {
        log_message <- paste0('Game ', game_id, ' added. ', custom_message)
      }
      else {
        log_message <- paste0('Game ', game_id, ' added.')
      }
    }
    log_data <- data.frame(date_added=c(Sys.Date(), Sys.Date()),
                           message=c(log_db_created_message, log_message),
                           signature=c(signature, signature))
    
    sheet_write(data=game_data, ss=ss_name, sheet='game_data')
    sheet_write(data=log_data, ss=ss_name, sheet='log')
    print(log_db_created_message)
    print(log_message)
  }
  else {
    print('ERROR - Fully tracked and partially tracked flags cannot both be true.')
  }
}

add_game <- function(game_id, signature, pt_data_fully_tracked=FALSE, pt_data_partially_tracked=FALSE, custom_message='') {
  # Adds a game to the database.
  # 
  # @description This function adds a game to the database, and adds a message to the log saying 
  # the game has been added.
  # 
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  # @param signature character. A signature for who added the game.
  # @param pt_data_fully_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is fully tracked or not.
  # @param pt_data_partially_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is partially tracked or not.
  # @param custom_message character. Optional, defaults to ''. A custom message to be added in the log message.
  # 
  # @details pt_data_fully_tracked and pt_data_partially_tracked cannot both be TRUE. If a game with the same game id already exists 
  # in the database, the game will not be added.
  if (!((pt_data_fully_tracked == TRUE) & (pt_data_partially_tracked == TRUE))) {
    game_db <- range_speedread(ss_name, sheet='game_data')
    if ((pt_data_fully_tracked == TRUE) | (pt_data_partially_tracked == TRUE)) {
      game_data_file <- paste0('~/baycats/pitches_tracked_game_data/', game_id, '_pt.csv')
    }
    else {
      game_data_file <- paste0('~/baycats/raw_game_data/', game_id, '.csv')
    }
    game_data <- read_csv(game_data_file)
    game_id <- unique(game_data$game_pk)
    only_game_id <- game_db %>%
      filter(game_pk == game_id)
    if (nrow(only_game_id) == 0) {
      if(pt_data_fully_tracked == TRUE) {
        if (custom_message != '') {
          log_message <- paste0('Game ', game_id, ' added. Pitch data fully tracked. ', custom_message)
        }
        else {
          log_message <- paste0('Game ', game_id, ' added. Pitch data fully tracked.')
        }
      }
      else if (pt_data_partially_tracked == TRUE) {
        if (custom_message != '') {
          log_message <- paste0('Game ', game_id, ' added. Pitch data partially tracked. ', custom_message)
        }
        else {
          log_message <- paste0('Game ', game_id, ' added. Pitch data partially tracked.')
        }
      }
      else {
        if (custom_message != '') {
          log_message <- paste0('Game ', game_id, ' added. ', custom_message)
        }
        else {
          log_message <- paste0('Game ', game_id, ' added.')
        }
      }
      log_data <- data.frame(date_added=c(Sys.Date()),
                             message=c(log_message),
                             signature=c(signature))
      
      sheet_append(ss_name, game_data, sheet='game_data')
      sheet_append(ss_name, log_data, sheet='log')
      print(log_message)
    }
    else {
      print('ERROR - Game is already found in database.')
    }
  }
  else {
    print('ERROR - Fully tracked and partially tracked flags cannot both be true.')
  }
}

write_began_pt_logging <- function(game_id, signature, custom_message='') {
  # Writes to the log saying a game has been started for pitch tracking.
  # 
  # @description This function adds a message to the log saying that the game has begun pitch tracking.
  # 
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  # @param signature character. A signature for who added the game.
  # @param custom_message character. Optional, defaults to ''. A custom message to be added in the log message.
  if (custom_message != '') {
    log_message <- paste0('Game ', game_id, ' has been started for pitch tracking. ', custom_message)
  }
  else {
    log_message <- paste0('Game ', game_id, ' has been started for pitch tracking.')
  }
  
  log_data <- data.frame(date_added=c(Sys.Date()),
                         message=c(log_message),
                         signature=c(signature))
  
  sheet_append(ss_name, log_data, sheet='log')
  print(log_message)
}

# READ

read_game_db <- function() {
  # Loads the game data into R.
  # 
  # @description Reads all of the game data in the database into the R session.
  game_db <- range_speedread(ss_name, sheet='game_data')
  return(game_data)
}

save_game_data <- function(game_id, pt_data_fully_tracked=FALSE, pt_data_partially_tracked=FALSE) {
  # Saves the data for one game in the database.
  # 
  # @description Searches the database and saves the game file for one game to the correct directory.
  #
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  # @param pt_data_fully_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is fully tracked or not.
  # @param pt_data_partially_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is partially tracked or not.
  #
  # @details if the game id is not found in the database then nothing will be returned.
  game_db <- range_speedread(ss_name, sheet='game_data')
  game_data <- game_db %>%
    filter(game_pk == game_id)
  if (nrow(game_data) != 0) {
    if ((pt_data_fully_tracked == TRUE) | (pt_data_partially_tracked == TRUE)) {
      write_csv(game_data, paste0('~/baycats/pitches_tracked_game_data/', game_id, '_pt.csv'))
      log_message <- paste0('Game ', game_id, 'saved to ~/baycats/pitches_tracked_game_data.')
    }
    else {
      write_csv(game_data, paste0('~/baycats/raw_game_data/', game_id, '.csv'))
      log_message <- paste0('Game ', game_id, 'saved to ~/baycats/raw_game_data.')
    }
    print(log_message)
  }
  else {
    print('ERROR - Game cannot be found in database.')
  }
}

view_game_pks <- function(search_game_date) {
  # Views all game ids for a date.
  # 
  # @description Prints all game ids of games on that day.
  # 
  # @param search_game_date character. The date that is being searched for in the form YYYY-MM-DD where YYYY is the year, MM is the month, and DD is the date.
  #
  # @details Will return an empty vector if no games are found for that date.
  game_data <- range_speedread(ss_name, sheet='game_data')
  only_game_date <- game_data %>%
    filter(game_date == search_game_date)
  print(unique(only_game_date$game_pk))
}

view_log_last_N <- function(N=15) {
  # Views the last N entries in the log.
  #
  # @description Prints the last N entries in the log.
  #
  # @param N numeric. Optional, defaults to 15. The number of entries to view.
  # 
  # @details The maximum number of entries that can be viewed is 15.
  log_data <- range_speedread(ss_name, sheet='log')
  if (N > 15) {
    print(tail(log_data, 15))
  }
  else {
    print(tail(log_data, N))
  }
}

search_log <- function(game_id) {
  # Searches the log for all entries about a single game.
  # 
  # @description Prints all entries in the log containing the game id.
  # 
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  #
  # @details Will print an empty string if there are no messages with the game id.
  log_data <- range_speedread(ss_name, sheet='log')
  print(log_data[grep(game_id, log_data$message), ])
}

# UPDATE

update_game <- function(game_id, signature, pt_data_fully_tracked=FALSE, pt_data_partially_tracked=FALSE, custom_message='') {
  # Updates the game data in the database.
  # 
  # @description Deletes the game from the database then adds the new game data and adds a message to the log saying that the game has been deleted, then the game has been added.
  # Used the delete_game function then the add_game function.
  #
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  # @param signature character. A signature for who updated the game.
  # @param pt_data_fully_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is fully tracked or not.
  # @param pt_data_partially_tracked boolean. Optional, defaults to FALSE. An indicator of whether the pitch tracking data is partially tracked or not.
  # @param custom_message character. Optional, defaults to ''. A custom message to be added in the log message.
  #
  # @details pt_data_fully_tracked and pt_data_partially_tracked cannot both be TRUE. If the game id cannot be found in the database then no data be deleted.
  if (custom_message != '') {
    custom_message <- paste0('Updated. ', custom_message)
  }
  else {
    custom_message <- 'Updated.'
  }
  delete_game(game_id, signature, custom_message)
  add_game(game_id, signature, pt_data_fully_tracked=pt_data_fully_tracked, pt_data_partially_tracked=pt_data_partially_tracked, custom_message)
}

# DELETE

delete_game <- function(game_id, signature, custom_message='') {
  # Deletes the data for the game from the database.
  #
  # @description Deletes the data containing the game id from the database.
  # 
  # @param game_id character. The id of the game. In the format YYYYMMDDRRRHHHN where YYYY is the year, 
  # MM is the month, DD is the date, RRR is the road team abbreviation, HHH is the home team abbreviation, 
  # N is the number of the game played between those two teams and is one unless the game is the second game of a doubleheader.
  # @param signature character. A signature for who deleted the game.
  # @param custom_message character. Optional, defaults to ''. A custom message to be added in the log message.
  #
  # @details If the game id cannot be found in the database then no data will be deleted.
  game_db <- range_speedread(ss_name, sheet='game_data')
  is_game_id <- function(x) {
    return(x == game_id)
  }
  only_game_id <- game_db %>%
    filter(game_pk == game_id)
  start_index <- detect_index(game_db$game_pk, is_game_id)
  if (start_index != 0) {
    if (custom_message != '') {
      log_message <- paste0('Game ', game_id, ' deleted. ', custom_message)
    }
    else {
      log_message <- paste0('Game ', game_id, ' deleted.')
    }
    log_data <- data.frame(date=c(Sys.Date()),
                           messgae=c(log_message),
                           signature=c(signature))
    
    if (start_index == 1) {
      delete_range <- paste0(2, ':', (nrow(only_game_id) + 1))
    }
    else {
      end_index <- start_index + nrow(only_game_id)
      delete_range <- paste0((start_index + 1), ':', end_index)
    }
    if (game_db[nrow(game_db), 'game_pk'] == game_id) {
      range_flood(ss_name, sheet='game_data', range=delete_range, reformat=TRUE)
    }
    else {
      range_delete(ss_name, range=delete_range)
    }

    sheet_append(ss_name, log_data, sheet='log')
    print(log_message)
  }
  else {
    print('ERROR - Game cannot be found in database.')
  }
  
}
