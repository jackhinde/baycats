library(tidyverse)
library(ggplot2)
library(shiny)
library(DT)
library(plotly)
library(htmlwidgets)

# ----------
# BEFORE RUNNING

# ENTER THE GAME ID IN QUOTATION MARKS
# IN THE FORM YYYYMMDDRRRHHHN
# YYYY is the year
# MM is the month
# DD is the date
# RRR is the road team abbreviation
# HHH is the home team abbreviation
# N is 1 if the game is not the second game of a doubleheader
# N is 2 if the game is the second game of a doubleheader
game_id <- '20230816BRABAR1'

# ENTER WHETHER PITCHES ARE PARTIALLY OR FULLY TRACKED
# TRUE if partially or fully tracked
# FALSE if not tracked at all
partially_or_fully_tracked <- TRUE
# ----------

{
  if (partially_or_fully_tracked == FALSE) {
    old_file_name <- paste0('~/baycats/raw_game_data/', game_id, '.csv')
  }
  else {
    old_file_name <- paste0('~/baycats/pitches_tracked_game_data/', game_id, '_pt.csv')
  }
}

old_data <- read_csv(old_file_name)

sz_right <- 9.97/12
sz_left <- -9.97/12
sz_top <- 44.08/12
sz_bottom <- 18.29/12
sz_middle <- (sz_top - sz_bottom)/2
zone_width <- (sz_right - sz_left)/3
zone_height <- (sz_top - sz_bottom)/3

h <- 2
theta <- seq(18.24, 161.76, length.out=50)
theta <- (pi/180)*theta
x <- 95*cos(theta)
y <- 95*sin(theta)
y <- y + 60.5
slope <- (-1)*(x/y)
x_left <- x - h
x_right <- x + h
y_left <- y - (h*slope)
y_right <- y + (h*slope)

infield_cut_df <- data.frame(
  x = x,
  y = y,
  slope = slope,
  x_left = x_left,
  x_right = x_right,
  y_left = y_left,
  y_right = y_right
)

get_zone <- function(x, z) {
  
  if ((is.na(x)) | (is.na(z))) {
    return(0)
  }
  else if ((x >= sz_left) & (x < (sz_left + zone_width)) & (z > (sz_top - zone_height)) & (z <= sz_top)) {
    return(1)
  }
  else if ((x >= (sz_left + zone_width)) & (x <= (sz_right - zone_width)) & (z > (sz_top - zone_height)) & (z <= sz_top)) {
    return(2)
  }
  else if ((x > (sz_right - zone_width)) & (x <= sz_right) & (z > (sz_top - zone_height)) & (z <= sz_top)) {
    return(3)
  }
  else if ((x >= sz_left) & (x < (sz_left + zone_width)) & (z >= (sz_bottom + zone_height)) & (z <= (sz_top - zone_height))) {
    return(4)
  }
  else if ((x >= (sz_left + zone_width)) & (x <= (sz_right - zone_width)) & (z >= (sz_bottom + zone_height)) & (z <= (sz_top - zone_height))) {
    return(5)
  }
  else if ((x > (sz_right - zone_width)) & (x <= sz_right) & (z >= (sz_bottom + zone_height)) & (z <= (sz_top - zone_height))) {
    return(6)
  }
  else if ((x >= sz_left) & (x < (sz_left + zone_width)) & (z >= sz_bottom) & (z < (sz_bottom + zone_height))) {
    return(7)
  }
  else if ((x >= (sz_left + zone_width)) & (x <= (sz_right - zone_width)) & (z >= sz_bottom) & (z < (sz_bottom + zone_height))) {
    return(8)
  }
  else if ((x > (sz_right - zone_width)) & (x <= sz_right) & (z >= sz_bottom) & (z < (sz_bottom + zone_height))) {
    return(9)
  }
  else if (((x < sz_left) & (z > sz_middle)) | ((x < 0) & (z > sz_top))) {
    return(10)
  }
  else if (((x > sz_right) & (z > sz_middle)) | ((x >= 0) & (z > sz_top))) {
    return(11)
  }
  else if (((x < sz_left) & (z <= sz_middle)) | ((x < 0) & (z < sz_bottom))) {
    return(12)
  }
  else if (((x > sz_right) & (z <= sz_middle)) | ((x >= 0) & (z < sz_bottom))) {
    return(13)
  }
  else {
    return(0)
  }
  
}

get_hit_distance_sc <- function(x, y) {
  
  if ((!is.na(x)) & (!is.na(y))) {
    return(sqrt((x^2) + (y^2)))
  }
  else {
    return(NaN)
  }
  
}

get_pitch_name <- function(pitch_type) {

  pitch_type_name_map <- c('CH'='Changeup', 
                           'CR'='Circle Change',
                           'CS'='Slow Curve', 
                           'CU'='Curveball',
                           'EP'='Eephus',
                           'FA'='Other',
                           'FC'='Cutter',
                           'FF'='Four-Seam Fastball',
                           'FO'='Forkball',
                           'FS'='Splitter',
                           'FT'='Two-Seam Fastball',
                           'KC'='Knuckle Curve',
                           'KN'='Knuckleball',
                           'PO'='Pitch Out',
                           'SC'='Screwball',
                           'SI'='Sinker',
                           'SL'='Slider',
                           'ST'='Sweeper',
                           'SV'='Slurve',
                           'UN'='Unknown')
  
  return(as.character(pitch_type_name_map[pitch_type]))

}

{
  if (!is.na(as.character(old_data[1, 'pitch_type']))) {
    start_pitch_type <- as.character(old_data[1, 'pitch_type'])
  }
  else {
    start_pitch_type <- '--'
  }
  if (!is.na(as.numeric(old_data[1, 'hit_location']))) {
    start_hit_location <- as.numeric(old_data[1, 'hit_location'])
  }
  else {
    start_hit_location <- as.numeric(NaN)
  } 
  if (!is.na(as.character(old_data[1, 'bb_type']))) {
    start_bb_type <- as.character(old_data[1, 'bb_type'])
  }
  else {
    start_bb_type <- as.character(NA)
  }
  if (!is.na(as.numeric(old_data[1, 'launch_speed_angle']))) {
    start_launch_speed_angle <- as.numeric(old_data[1, 'launch_speed_angle'])
  }
  else {
    start_launch_speed_angle <- as.numeric(NaN)
  }
  if ((!is.na(as.numeric(old_data[1, 'plate_x']))) & (!is.na(as.numeric(old_data[1, 'plate_z'])))) {
    start_sz_x <- as.numeric(old_data[1, 'plate_x'])
    start_sz_z <- as.numeric(old_data[1, 'plate_z'])
  }
  else {
    start_sz_x <- as.numeric(NaN)
    start_sz_z <- as.numeric(NaN)
  }
  if ((!is.na(as.numeric(old_data[1, 'hc_x']))) & (!is.na(as.numeric(old_data[1, 'hc_y'])))) {
    start_field_x <- as.numeric(old_data[1, 'hc_x'])
    start_field_y <- as.numeric(old_data[1, 'hc_y'])
  }
  else {
    start_field_x <- as.numeric(NaN)
    start_field_y <- as.numeric(NaN)
  }
}

ui <- fluidPage(
  
  # Application title
  titlePanel(""),
  
  sidebarLayout(
    
    sidebarPanel(
      
      radioButtons('sz_view', label='Strike Zone View',
                   choices=c('Catcher' = 'catcher', 'Pitcher' = 'pitcher'),
                   selected='catcher'),
      
      selectInput('pitch_type', label='Pitch Type',
                  choices=c('--' = '--', 
                           'Changeup' = 'CH', 
                           'Circle Change' = 'CR',
                           'Curveball' = 'CU',
                           'Cutter' = 'FC',
                           'Eephus' = 'EP',
                           'Other' = 'FA',
                           'Forkball' = 'FO',
                           'Four-Seam Fastball' = 'FF',
                           'Knuckle Curve' = 'KC',
                           'Knuckleball' = 'KN',
                           'Pitch Out' = 'PO',
                           'Screwball' = 'SC',
                           'Sinker' = 'SI',
                           'Slider' = 'SL',
                           'Slow Curve' = 'CS',
                           'Slurve' = 'SV',
                           'Splitter' = 'FS',
                           'Sweeper' = 'ST',
                           'Two-Seam Fastball' = 'FT',
                           'Unknown' = 'UN'),
                  selected=start_pitch_type),
      
      selectInput('hit_location', label='Hit Location',
                  choices=c('Not Hit Into Play' = NaN,
                            'P' = 1, 
                            'C' = 2, 
                            '1B' = 3, 
                            '2B' = 4, 
                            '3B' = 5, 
                            'SS' = 6, 
                            'LF' = 7, 
                            'CF' = 8, 
                            'RF' = 9,
                            'Unknown' = 0),
                  selected=start_hit_location),
      
      selectInput('bb_type', label='Batted Ball Type',
                  choices=c('Not Hit Into Play' = NA,
                            'Bunt' = 'bunt',
                            'Fly Ball' = 'fly_ball',
                            'Ground Ball' = 'ground_ball',
                            'Line Drive' = 'line_drive',
                            'Popup' = 'popup',
                            'Unknown' = 'unknown'),
                  selected=start_bb_type),
      
      selectInput('launch_speed_angle', label='Launch Speed/Angle',
                  choices=c('Not Hit Into Play' = NaN,
                            'Weak' = 1,
                            'Topped' = 2,
                            'Under' = 3,
                            'Flare/Burner' = 4,
                            'Solid Contact' = 5,
                            'Barrel' = 6,
                            'Unknown' = 0),
                  selected=start_launch_speed_angle),
      
      actionButton('prev_pitch', 'Previous'),
      
      actionButton('next_pitch', 'Next'),
      
      actionButton('done_tracking', 'Done'),
      
      numericInput('ffwd_inning', label='Fast Forward to Inning', 
                   value=1, 
                   min=min(old_data$inning), 
                   max=max(old_data$inning), 
                   step=1),
      
      radioButtons('ffwd_topbot', label='Fast Forward to Top/Bottom', 
                   choices=c('Top' = 'Top', 'Bottom' = 'Bot'), 
                   selected='Top'),
      
      actionButton('ffwd', 'Fast Forward'),
      
      width=4
      
    ),
    
    mainPanel(
      
      fluidRow(splitLayout(cellwidths=c('50%', '50%'), plotlyOutput('strike_zone'), plotlyOutput('field_layout'))),
      
      fluidRow(dataTableOutput('pitch_data_1')),
      
      fluidRow(dataTableOutput('pitch_data_2')),
      
      fluidRow(splitLayout(cellwidths=c('33%', '33%', '33%'), textOutput('sz_label'), verbatimTextOutput('click_sz_x'), verbatimTextOutput('click_sz_z'))),
      
      fluidRow(splitLayout(cellwidths=c('33%', '33%', '33%'), textOutput('field_label'), verbatimTextOutput('click_field_x'), verbatimTextOutput('click_field_y')))
      
    )
    
  )
  
)

server = function(input, output, session) {
  
  js <- "
    function(el, x, inputName){
      var id = el.getAttribute('id');
      var gd = document.getElementById(id);
      var d3 = Plotly.d3;
      Plotly.update(id).then(attach);
        function attach() {
          gd.addEventListener('click', function(evt) {
            var xaxis = gd._fullLayout.xaxis;
            var yaxis = gd._fullLayout.yaxis;
            var bb = evt.target.getBoundingClientRect();
            var x = xaxis.p2d(evt.clientX - bb.left);
            var y = yaxis.p2d(evt.clientY - bb.top);
            var coordinates = [x, y];
            Shiny.setInputValue(inputName, coordinates);
          });
        };
  }
  "
  
  df_index <- reactiveVal(1)
  
  game_data <- reactiveVal(old_data)
  
  clickposition_sz_x <- reactiveVal(start_sz_x)
  clickposition_sz_z <- reactiveVal(start_sz_z)
  
  clickposition_field_x <- reactiveVal(start_field_x)
  clickposition_field_y <- reactiveVal(start_field_y)
  
  observeEvent(input$clickposition_sz, {
    if (input$sz_view == 'pitcher') {
      clickposition_sz_x((-1)*(as.numeric(input$clickposition_sz[1])))
    }
    else {
      clickposition_sz_x(as.numeric(input$clickposition_sz[1]))
    }
    clickposition_sz_z(as.numeric(input$clickposition_sz[2]))
    temp_data <- game_data()
    temp_data[df_index(), 'plate_x'] <- clickposition_sz_x()
    temp_data[df_index(), 'plate_z'] <- clickposition_sz_z()
    game_data(temp_data)
  })
  
  observeEvent(input$clickposition_field, {
    clickposition_field_x(as.numeric(input$clickposition_field[1]))
    clickposition_field_y(as.numeric(input$clickposition_field[2]))
    temp_data <- game_data()
    temp_data[df_index(), 'hc_x'] <- clickposition_field_x()
    temp_data[df_index(), 'hc_y'] <- clickposition_field_y()
    game_data(temp_data)
  })
  
  observeEvent(input$prev_pitch, {
    if (df_index() == 1) {
      showNotification('No previous pitches.', type='error')
    }
    else {
      new_df_index <- df_index() - 1
      
      df_index(new_df_index)
      
      updateSelectInput(session,
                        'pitch_type', label='Pitch Type',
                        choices=c('--' = '--', 
                                  'Changeup' = 'CH', 
                                  'Circle Change' = 'CR',
                                  'Curveball' = 'CU',
                                  'Cutter' = 'FC',
                                  'Eephus' = 'EP',
                                  'Other' = 'FA',
                                  'Forkball' = 'FO',
                                  'Four-Seam Fastball' = 'FF',
                                  'Knuckle Curve' = 'KC',
                                  'Knuckleball' = 'KN',
                                  'Pitch Out' = 'PO',
                                  'Screwball' = 'SC',
                                  'Sinker' = 'SI',
                                  'Slider' = 'SL',
                                  'Slow Curve' = 'CS',
                                  'Slurve' = 'SV',
                                  'Splitter' = 'FS',
                                  'Sweeper' = 'ST',
                                  'Two-Seam Fastball' = 'FT',
                                  'Unknown' = 'UN'),
                        selected=as.character(game_data()[df_index(), 'pitch_type']))
      
      if (!is.na(as.numeric(game_data()[df_index(), 'hit_location']))) {
        updateSelectInput(session,
                          'hit_location', label='Hit Location',
                          choices=c('Not Hit Into Play' = NaN,
                                    'P' = 1, 
                                    'C' = 2, 
                                    '1B' = 3, 
                                    '2B' = 4, 
                                    '3B' = 5, 
                                    'SS' = 6, 
                                    'LF' = 7, 
                                    'CF' = 8, 
                                    'RF' = 9,
                                    'Unknown' = 0),
                          selected=as.numeric(game_data()[df_index(), 'hit_location']))
      }
      else {
        updateSelectInput(session,
                          'hit_location', label='Hit Location',
                          choices=c('Not Hit Into Play' = NaN,
                                    'P' = 1, 
                                    'C' = 2, 
                                    '1B' = 3, 
                                    '2B' = 4, 
                                    '3B' = 5, 
                                    'SS' = 6, 
                                    'LF' = 7, 
                                    'CF' = 8, 
                                    'RF' = 9,
                                    'Unknown' = 0))
      }
      
      if (!is.na(as.character(game_data()[df_index(), 'bb_type']))) {
        updateSelectInput(session,
                          'bb_type', label='Batted Ball Type',
                          choices=c('Not Hit Into Play' = NA,
                                    'Bunt' = 'bunt',
                                    'Fly Ball' = 'fly_ball',
                                    'Ground Ball' = 'ground_ball',
                                    'Line Drive' = 'line_drive',
                                    'Popup' = 'popup',
                                    'Unknown' = 'unknown'),
                          selected=as.character(game_data()[df_index(), 'bb_type']))
      }
      else {
        updateSelectInput(session,
                          'bb_type', label='Batted Ball Type',
                          choices=c('Not Hit Into Play' = NA,
                                    'Bunt' = 'bunt',
                                    'Fly Ball' = 'fly_ball',
                                    'Ground Ball' = 'ground_ball',
                                    'Line Drive' = 'line_drive',
                                    'Popup' = 'popup',
                                    'Unknown' = 'unknown'))
      }
      
      if (!is.na(as.numeric(game_data()[df_index(), 'launch_speed_angle']))) {
        updateSelectInput(session,
                          'launch_speed_angle', label='Launch Speed/Angle',
                          choices=c('Not Hit Into Play' = NaN,
                                    'Weak' = 1,
                                    'Topped' = 2,
                                    'Under' = 3,
                                    'Flare/Burner' = 4,
                                    'Solid Contact' = 5,
                                    'Barrel' = 6,
                                    'Unknown' = 0),
                          selected=as.numeric(game_data()[df_index(), 'launch_speed_angle']))
      }
      else {
        updateSelectInput(session,
                          'launch_speed_angle', label='Launch Speed/Angle',
                          choices=c('Not Hit Into Play' = NaN,
                                    'Weak' = 1,
                                    'Topped' = 2,
                                    'Under' = 3,
                                    'Flare/Burner' = 4,
                                    'Solid Contact' = 5,
                                    'Barrel' = 6,
                                    'Unknown' = 0))
      }
      
      clickposition_sz_x(as.numeric(game_data()[df_index(), 'plate_x']))
      clickposition_sz_z(as.numeric(game_data()[df_index(), 'plate_z']))
      clickposition_field_x(as.numeric(game_data()[df_index(), 'hc_x']))
      clickposition_field_y(as.numeric(game_data()[df_index(), 'hc_y']))
      
    }
  })
  
  observeEvent(input$next_pitch, {
    if (df_index() == nrow(game_data())) {
      showNotification('No more pitches in game.', type='error')
    }
    else {
      if (input$pitch_type == '--') {
        showNotification('Pitch Type field is empty. Select \'Unknown\' if the value cannot be input.', type='error')
      }
      else if ((game_data()[df_index(), 'type'] == 'X') & ((is.na(input$hit_location)) | (is.na(input$bb_type)) | (is.na(input$launch_speed_angle)))) {
        showNotification('One or more necessary fields are empty. Select \'Unknown\' if the value cannot be input.', type='error')
      }
      else {
        updated_data <- game_data()
        updated_data[df_index(), 'pitch_type'] <- as.character(input$pitch_type)
        updated_data[df_index(), 'plate_x'] <- as.numeric(clickposition_sz_x())
        updated_data[df_index(), 'plate_z'] <- as.numeric(clickposition_sz_z())
        updated_data[df_index(), 'hc_x'] <- as.numeric(clickposition_field_x())
        updated_data[df_index(), 'hc_y'] <- as.numeric(clickposition_field_y())
        updated_data[df_index(), 'hit_location'] <- as.numeric(input$hit_location)
        updated_data[df_index(), 'bb_type'] <- as.character(input$bb_type)
        updated_data[df_index(), 'launch_speed_angle'] <- as.numeric(input$launch_speed_angle)
        
        updated_data[df_index(), 'zone'] <- get_zone(as.numeric(clickposition_sz_x()), as.numeric(clickposition_sz_z()))
        updated_data[df_index(), 'hit_distance_sc'] <- get_hit_distance_sc(as.numeric(clickposition_field_x()), as.numeric(clickposition_field_y()))
        updated_data[df_index(), 'pitch_name'] <- get_pitch_name(as.character(input$pitch_type))
        
        game_data(updated_data)
        
        new_df_index <- df_index() + 1
        
        df_index(new_df_index)
        
        if (!is.na(as.character(game_data()[df_index(), 'pitch_type']))) {
          updateSelectInput(session,
                            'pitch_type', label='Pitch Type',
                            choices=c('--' = '--', 
                                      'Changeup' = 'CH', 
                                      'Circle Change' = 'CR',
                                      'Curveball' = 'CU',
                                      'Cutter' = 'FC',
                                      'Eephus' = 'EP',
                                      'Other' = 'FA',
                                      'Forkball' = 'FO',
                                      'Four-Seam Fastball' = 'FF',
                                      'Knuckle Curve' = 'KC',
                                      'Knuckleball' = 'KN',
                                      'Pitch Out' = 'PO',
                                      'Screwball' = 'SC',
                                      'Sinker' = 'SI',
                                      'Slider' = 'SL',
                                      'Slow Curve' = 'CS',
                                      'Slurve' = 'SV',
                                      'Splitter' = 'FS',
                                      'Sweeper' = 'ST',
                                      'Two-Seam Fastball' = 'FT',
                                      'Unknown' = 'UN'),
                            selected=as.character(game_data()[df_index(), 'pitch_type']))
        }
        else {
          updateSelectInput(session,
                            'pitch_type', label='Pitch Type',
                            choices=c('--' = '--', 
                                      'Changeup' = 'CH', 
                                      'Circle Change' = 'CR',
                                      'Curveball' = 'CU',
                                      'Cutter' = 'FC',
                                      'Eephus' = 'EP',
                                      'Other' = 'FA',
                                      'Forkball' = 'FO',
                                      'Four-Seam Fastball' = 'FF',
                                      'Knuckle Curve' = 'KC',
                                      'Knuckleball' = 'KN',
                                      'Pitch Out' = 'PO',
                                      'Screwball' = 'SC',
                                      'Sinker' = 'SI',
                                      'Slider' = 'SL',
                                      'Slow Curve' = 'CS',
                                      'Slurve' = 'SV',
                                      'Splitter' = 'FS',
                                      'Sweeper' = 'ST',
                                      'Two-Seam Fastball' = 'FT',
                                      'Unknown' = 'UN'),
                            selected='--')
        }
        
        if (!is.na(as.numeric(game_data()[df_index(), 'hit_location']))) {
          updateSelectInput(session,
                            'hit_location', label='Hit Location',
                            choices=c('Not Hit Into Play' = NaN,
                                      'P' = 1, 
                                      'C' = 2, 
                                      '1B' = 3, 
                                      '2B' = 4, 
                                      '3B' = 5, 
                                      'SS' = 6, 
                                      'LF' = 7, 
                                      'CF' = 8, 
                                      'RF' = 9,
                                      'Unknown' = 0),
                            selected=as.numeric(game_data()[df_index(), 'hit_location']))
        }
        else {
          updateSelectInput(session,
                            'hit_location', label='Hit Location',
                            choices=c('Not Hit Into Play' = NaN,
                                      'P' = 1, 
                                      'C' = 2, 
                                      '1B' = 3, 
                                      '2B' = 4, 
                                      '3B' = 5, 
                                      'SS' = 6, 
                                      'LF' = 7, 
                                      'CF' = 8, 
                                      'RF' = 9,
                                      'Unknown' = 0))
        }
        
        if (!is.na(as.character(game_data()[df_index(), 'bb_type']))) {
          updateSelectInput(session,
                            'bb_type', label='Batted Ball Type',
                            choices=c('Not Hit Into Play' = NA,
                                      'Bunt' = 'bunt',
                                      'Fly Ball' = 'fly_ball',
                                      'Ground Ball' = 'ground_ball',
                                      'Line Drive' = 'line_drive',
                                      'Popup' = 'popup',
                                      'Unknown' = 'unknown'),
                            selected=as.character(game_data()[df_index(), 'bb_type']))
        }
        else {
          updateSelectInput(session,
                            'bb_type', label='Batted Ball Type',
                            choices=c('Not Hit Into Play' = NA,
                                      'Bunt' = 'bunt',
                                      'Fly Ball' = 'fly_ball',
                                      'Ground Ball' = 'ground_ball',
                                      'Line Drive' = 'line_drive',
                                      'Popup' = 'popup',
                                      'Unknown' = 'unknown'))
        }
        
        if (!is.na(as.numeric(game_data()[df_index(), 'launch_speed_angle']))) {
          updateSelectInput(session,
                            'launch_speed_angle', label='Launch Speed/Angle',
                            choices=c('Not Hit Into Play' = NaN,
                                      'Weak' = 1,
                                      'Topped' = 2,
                                      'Under' = 3,
                                      'Flare/Burner' = 4,
                                      'Solid Contact' = 5,
                                      'Barrel' = 6,
                                      'Unknown' = 0),
                            selected=as.numeric(game_data()[df_index(), 'launch_speed_angle']))
        }
        else {
          updateSelectInput(session,
                            'launch_speed_angle', label='Launch Speed/Angle',
                            choices=c('Not Hit Into Play' = NaN,
                                      'Weak' = 1,
                                      'Topped' = 2,
                                      'Under' = 3,
                                      'Flare/Burner' = 4,
                                      'Solid Contact' = 5,
                                      'Barrel' = 6,
                                      'Unknown' = 0))
        }
        
        if ((!is.na(as.numeric(game_data()[df_index(), 'plate_x']))) & (!is.na(as.numeric(game_data()[df_index(), 'plate_z'])))) {
          clickposition_sz_x(as.numeric(game_data()[df_index(), 'plate_x']))
          clickposition_sz_z(as.numeric(game_data()[df_index(), 'plate_z']))
        }
        else {
          clickposition_sz_x(as.numeric(NaN))
          clickposition_sz_z(as.numeric(NaN))
        }
        
        if ((!is.na(game_data()[df_index(), 'hc_x'])) & (!is.na(game_data()[df_index(), 'hc_y']))) {
          clickposition_field_x(as.numeric(game_data()[df_index(), 'hc_x']))
          clickposition_field_y(as.numeric(game_data()[df_index(), 'hc_y']))
        }
        else {
          clickposition_field_x(as.numeric(NaN))
          clickposition_field_y(as.numeric(NaN))
        }
      }
    }
  })
  
  observeEvent(input$done_tracking, {
    if (input$pitch_type == '--') {
      showNotification('Pitch Type field is empty. Select \'Unknown\' if the value cannot be input.', type='error')
    }
    else if ((game_data()[df_index(), 'type'] == 'X') & ((is.na(input$hit_location)) | (is.na(input$bb_type)) | (is.na(input$launch_speed_angle)))) {
      showNotification('One or more necessary fields are empty. Select \'Unknown\' if the value cannot be input.', type='error')
    }
    else {
      updated_data <- game_data()
      updated_data[df_index(), 'pitch_type'] <- as.character(input$pitch_type)
      updated_data[df_index(), 'plate_x'] <- as.numeric(clickposition_sz_x())
      updated_data[df_index(), 'plate_z'] <- as.numeric(clickposition_sz_z())
      updated_data[df_index(), 'hc_x'] <- as.numeric(clickposition_field_x())
      updated_data[df_index(), 'hc_y'] <- as.numeric(clickposition_field_y())
      updated_data[df_index(), 'hit_location'] <- as.numeric(input$hit_location)
      updated_data[df_index(), 'bb_type'] <- as.character(input$bb_type)
      updated_data[df_index(), 'launch_speed_angle'] <- as.numeric(input$launch_speed_angle)
      
      updated_data[df_index(), 'zone'] <- get_zone(as.numeric(clickposition_sz_x()), as.numeric(clickposition_sz_z()))
      updated_data[df_index(), 'hit_distance_sc'] <- get_hit_distance_sc(as.numeric(clickposition_field_x()), as.numeric(clickposition_field_y()))
      updated_data[df_index(), 'pitch_name'] <- get_pitch_name(as.character(input$pitch_type))
      
      game_data(updated_data)
    }
    
    write_csv(game_data(), paste0('~/baycats/pitches_tracked_game_data/', game_id, '_pt.csv'), na='')
    
    stopApp()
  })
  
  observeEvent(input$ffwd, {
    is_inning <- function(x) {
      return(x == input$ffwd_inning)
    }
    
    is_topbot <- function(x) {
      return(x == input$ffwd_topbot)
    }

    filtered_data <- game_data()
    
    start_index_inning <- detect_index(filtered_data$inning, is_inning)
    
    start_index_topbot <- detect_index(pull(filter(filtered_data, inning == input$ffwd_inning), inning_topbot), is_topbot)
    
    if (start_index_topbot == 0) {
      showNotification('Game data does not exist for this half inning.', type='error')
    }
    else {
      new_df_index <- start_index_inning + (start_index_topbot - 1)
      
      df_index(new_df_index)
      
      if (!is.na(as.character(game_data()[df_index(), 'pitch_type']))) {
        updateSelectInput(session,
                          'pitch_type', label='Pitch Type',
                          choices=c('--' = '--', 
                                    'Changeup' = 'CH', 
                                    'Circle Change' = 'CR',
                                    'Curveball' = 'CU',
                                    'Cutter' = 'FC',
                                    'Eephus' = 'EP',
                                    'Other' = 'FA',
                                    'Forkball' = 'FO',
                                    'Four-Seam Fastball' = 'FF',
                                    'Knuckle Curve' = 'KC',
                                    'Knuckleball' = 'KN',
                                    'Pitch Out' = 'PO',
                                    'Screwball' = 'SC',
                                    'Sinker' = 'SI',
                                    'Slider' = 'SL',
                                    'Slow Curve' = 'CS',
                                    'Slurve' = 'SV',
                                    'Splitter' = 'FS',
                                    'Sweeper' = 'ST',
                                    'Two-Seam Fastball' = 'FT',
                                    'Unknown' = 'UN'),
                          selected=as.character(game_data()[df_index(), 'pitch_type']))
      }
      else {
        updateSelectInput(session,
                          'pitch_type', label='Pitch Type',
                          choices=c('--' = '--', 
                                    'Changeup' = 'CH', 
                                    'Circle Change' = 'CR',
                                    'Curveball' = 'CU',
                                    'Cutter' = 'FC',
                                    'Eephus' = 'EP',
                                    'Other' = 'FA',
                                    'Forkball' = 'FO',
                                    'Four-Seam Fastball' = 'FF',
                                    'Knuckle Curve' = 'KC',
                                    'Knuckleball' = 'KN',
                                    'Pitch Out' = 'PO',
                                    'Screwball' = 'SC',
                                    'Sinker' = 'SI',
                                    'Slider' = 'SL',
                                    'Slow Curve' = 'CS',
                                    'Slurve' = 'SV',
                                    'Splitter' = 'FS',
                                    'Sweeper' = 'ST',
                                    'Two-Seam Fastball' = 'FT',
                                    'Unknown' = 'UN'),
                          selected='--')
      }
      
      if(!is.na(as.numeric(game_data()[df_index(), 'hit_location']))) {
        updateSelectInput(session,
                          'hit_location', label='Hit Location',
                          choices=c('Not Hit Into Play' = NaN,
                                    'P' = 1, 
                                    'C' = 2, 
                                    '1B' = 3, 
                                    '2B' = 4, 
                                    '3B' = 5, 
                                    'SS' = 6, 
                                    'LF' = 7, 
                                    'CF' = 8, 
                                    'RF' = 9,
                                    'Unknown' = 0),
                          selected=as.numeric(game_data()[df_index(), 'hit_location']))
      }
      else {
        updateSelectInput(session,
                          'hit_location', label='Hit Location',
                          choices=c('Not Hit Into Play' = NaN,
                                    'P' = 1, 
                                    'C' = 2, 
                                    '1B' = 3, 
                                    '2B' = 4, 
                                    '3B' = 5, 
                                    'SS' = 6, 
                                    'LF' = 7, 
                                    'CF' = 8, 
                                    'RF' = 9,
                                    'Unknown' = 0))
      }
      
      if(!is.na(as.character(game_data()[df_index(), 'bb_type']))) {
        updateSelectInput(session,
                          'bb_type', label='Batted Ball Type',
                          choices=c('Not Hit Into Play' = NA,
                                    'Bunt' = 'bunt',
                                    'Fly Ball' = 'fly_ball',
                                    'Ground Ball' = 'ground_ball',
                                    'Line Drive' = 'line_drive',
                                    'Popup' = 'popup',
                                    'Unknown' = 'unknown'),
                          selected=as.character(game_data()[df_index(), 'bb_type']))
      }
      else {
        updateSelectInput(session,
                          'bb_type', label='Batted Ball Type',
                          choices=c('Not Hit Into Play' = NA,
                                    'Bunt' = 'bunt',
                                    'Fly Ball' = 'fly_ball',
                                    'Ground Ball' = 'ground_ball',
                                    'Line Drive' = 'line_drive',
                                    'Popup' = 'popup',
                                    'Unknown' = 'unknown'))
      }
      
      if(!is.na(as.numeric(game_data()[df_index(), 'launch_speed_angle']))) {
        updateSelectInput(session,
                          'launch_speed_angle', label='Launch Speed/Angle',
                          choices=c('Not Hit Into Play' = NaN,
                                    'Weak' = 1,
                                    'Topped' = 2,
                                    'Under' = 3,
                                    'Flare/Burner' = 4,
                                    'Solid Contact' = 5,
                                    'Barrel' = 6,
                                    'Unknown' = 0),
                          selected=as.numeric(game_data()[df_index(), 'launch_speed_angle']))
      }
      else {
        updateSelectInput(session,
                          'launch_speed_angle', label='Launch Speed/Angle',
                          choices=c('Not Hit Into Play' = NaN,
                                    'Weak' = 1,
                                    'Topped' = 2,
                                    'Under' = 3,
                                    'Flare/Burner' = 4,
                                    'Solid Contact' = 5,
                                    'Barrel' = 6,
                                    'Unknown' = 0))
      }
      
      if ((!is.na(as.numeric(game_data()[df_index(), 'plate_x']))) & (!is.na(as.numeric(game_data()[df_index(), 'plate_z'])))) {
        clickposition_sz_x(as.numeric(game_data()[df_index(), 'plate_x']))
        clickposition_sz_z(as.numeric(game_data()[df_index(), 'plate_z']))
      }
      else {
        clickposition_sz_x(as.numeric(NaN))
        clickposition_sz_z(as.numeric(NaN))
      }
      
      if ((!is.na(game_data()[df_index(), 'hc_x'])) & (!is.na(game_data()[df_index(), 'hc_y']))) {
        clickposition_field_x(as.numeric(game_data()[df_index(), 'hc_x']))
        clickposition_field_y(as.numeric(game_data()[df_index(), 'hc_y']))
      }
      else {
        clickposition_field_x(as.numeric(NaN))
        clickposition_field_y(as.numeric(NaN))
      }
      
      updateNumericInput(session,
                         'ffwd_inning', label='Fast Forward to Inning', 
                         value=1,
                         min=min(game_data()$inning), 
                         max=max(game_data()$inning), 
                         step=1)
      
      updateRadioButtons(session,
                   'ffwd_topbot', label='Fast Forward to Top/Bottom', 
                   choices=c('Top' = 'Top', 'Bottom' = 'Bot'), 
                   selected='Top')
      
    }
    
  })
  
  output$strike_zone <- renderPlotly({
    
    sz_plot <- ggplot((game_data() %>% slice(df_index())), aes(x=as.numeric(plate_x), y=as.numeric(plate_z))) +
      geom_point(colour='red') +
      
      geom_segment(x = sz_left, y = sz_top, xend = sz_right, yend = sz_top) +
      geom_segment(x = sz_left, y = sz_bottom, xend = sz_right, yend = sz_bottom) +
      geom_segment(x = sz_left, y = sz_top, xend = sz_left, yend = sz_bottom) +
      geom_segment(x = sz_right, y = sz_top, xend = sz_right, yend = sz_bottom) +
      
      geom_segment(x = sz_left, y = (sz_bottom + zone_height), xend = sz_right, yend = (sz_bottom + zone_height)) +
      geom_segment(x = sz_left, y = (sz_top - zone_height), xend = sz_right, yend = (sz_top - zone_height)) +
      geom_segment(x = (sz_left + zone_width), y = sz_bottom, xend = (sz_left + zone_width), yend = sz_top) +
      geom_segment(x = (sz_right - zone_width), y = sz_bottom, xend = (sz_right - zone_width), yend = sz_top)
      
      # geom_segment(x = (-8.5/12), y = 0, xend = (8.5/12), yend = 0) +
      # geom_segment(x = (8.5/12), y = 0, xend = (8.5/12), yend = (-4.25/12)) +
      # geom_segment(x = (8.5/12), y = (-4.25/12), xend = 0, yend = (-8.5/12)) +
      # geom_segment(x = 0, y = (-8.5/12), xend = (-8.5/12), yend = (-4.25/12)) +
      # geom_segment(x = (-8.5/12), y = (-4.25/12), xend = (-8.5/12), yend = 0) +
      # 
      # theme(plot.title = element_blank(),
      #       panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
      #       panel.background = element_blank(),
      #       legend.position = 'none',
      #       axis.title.x = element_blank(),
      #       axis.title.y = element_blank()) + 
      # xlim(-2.5,2.5) + ylim((-8.5/12), 5)
    
    if (input$sz_view == 'pitcher') {
      sz_plot <- sz_plot + 
        scale_x_reverse() +
        geom_segment(x = (8.5/12), y = 0, xend = (-8.5/12), yend = 0) +
        geom_segment(x = (-8.5/12), y = 0, xend = (-8.5/12), yend = (4.25/12)) +
        geom_segment(x = (-8.5/12), y = (4.25/12), xend = 0, yend = (8.5/12)) +
        geom_segment(x = 0, y = (8.5/12), xend = (8.5/12), yend = (4.25/12)) +
        geom_segment(x = (8.5/12), y = (4.25/12), xend = (8.5/12), yend = 0) +
        
        theme(plot.title = element_blank(),
              panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
              panel.background = element_blank(),
              legend.position = 'none',
              axis.title.x = element_blank(),
              axis.title.y = element_blank()) + 
        xlim(2.5, -2.5) + ylim((-8.5/12), 5)
    }
    
    else {
      sz_plot <- sz_plot + 
        geom_segment(x = (-8.5/12), y = 0, xend = (8.5/12), yend = 0) +
        geom_segment(x = (8.5/12), y = 0, xend = (8.5/12), yend = (-4.25/12)) +
        geom_segment(x = (8.5/12), y = (-4.25/12), xend = 0, yend = (-8.5/12)) +
        geom_segment(x = 0, y = (-8.5/12), xend = (-8.5/12), yend = (-4.25/12)) +
        geom_segment(x = (-8.5/12), y = (-4.25/12), xend = (-8.5/12), yend = 0) +
        
        theme(plot.title = element_blank(),
              panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
              panel.background = element_blank(),
              legend.position = 'none',
              axis.title.x = element_blank(),
              axis.title.y = element_blank()) + 
        xlim(-2.5,2.5) + ylim((-8.5/12), 5)
    }
    
    ggplotly(sz_plot, tooltip=NULL) %>%
      onRender(js, data='clickposition_sz')
    
  })
  
  output$field_layout <- renderPlotly({
    
    field_plot <- ggplot((game_data() %>% slice(df_index())), aes(x=as.numeric(hc_x), y=as.numeric(hc_y))) +
      
      geom_point(colour='red') +
      
      geom_segment(x = 0, y = 0, xend = 229.81, yend = 229.81) +
      geom_segment(x = 0, y = 0, xend = -229.81, yend = 229.81) +
      
      geom_segment(x = 63.64, y = 63.64, xend = 0, yend = 127.28) +
      geom_segment(x = -63.64, y = 63.64, xend = 0, yend = 127.28) +
      
      geom_segment(x = -1, y = 60.5, xend = 1, yend = 60.5) +
      geom_segment(x = -1, y = 61, xend = 1, yend = 61) +
      geom_segment(x = -1, y = 60.5, xend = -1, yend = 61) +
      geom_segment(x = 1, y = 60.5, xend = 1, yend = 61) +
      
      geom_segment(aes(x = x_left, y = y_left, xend = x_right, yend = y_right), data=infield_cut_df) +
      
      # geom_curve(x = 229.81, y = 229.81, xend = -229.81, yend = 229.81, curvature = 0.725, angle = 90) +
      # geom_curve(x = 89.73, y = 89.73, xend = -89.73, yend = 89.73, curvature = 0.75, angle = 90) +
      
      theme(plot.title = element_blank(),
            panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
            panel.background = element_blank(),
            legend.position = 'none',
            axis.title.x = element_blank(),
            axis.title.y = element_blank()) + 
      xlim(-300, 300) + ylim(-60, 450)
     
    ggplotly(field_plot, tooltip=NULL) %>%
      onRender(js, data='clickposition_field')
    
  })
  
  output$pitch_data_1 <- renderDataTable(
    
    game_data() %>% select(batter, pitcher, balls, strikes, 
                           outs_when_up, inning, inning_topbot, stand,
                           p_throws) %>% 
      slice(df_index()),
    
    options=list(info=FALSE, lengthChange=FALSE, ordering=FALSE, paging=FALSE, searching=FALSE)
    
  )
  
  output$pitch_data_2 <- renderDataTable(
    
    game_data() %>% select(type, description, events, pitch_number,
                           home_score, away_score, bat_score, fld_score) %>% 
      slice(df_index()),
    
    options=list(info=FALSE, lengthChange=FALSE, ordering=FALSE, paging=FALSE, searching=FALSE)
    
  )
  
  output$sz_label <- renderText({
    'plate_x, plate_z'
  })
  
  output$field_label <- renderText({
    'hc_x, hc_y'
  })
  
  output$click_sz_x <- renderPrint({
    clickposition_sz_x()
  })
  
  output$click_sz_z <- renderPrint({
    clickposition_sz_z()
  })
  
  output$click_field_x <- renderPrint({
    clickposition_field_x()
  })
  
  output$click_field_y <- renderPrint({
    clickposition_field_y()
  })
  
}

shinyApp(ui=ui, server=server)