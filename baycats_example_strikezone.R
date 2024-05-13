library(tidyverse)
library(ggplot2)
library(shiny)
library(shinythemes)

data <- read_csv('chw_2023_first_two_games.csv')

data <- data %>%
  mutate(pitcher_team = case_when(
    inning_topbot == 'Top' ~ home_team,
    inning_topbot == 'Bot' ~ away_team,
    .default = ''
           ))

data <- data %>%
  filter(!(pitch_name %in% c('', 'Eephus', 'Pitch Out', 'Other', 'Screwball', 'Knuckleball')))

data <- data %>%
  mutate(pitch_name = case_when(
    pitch_name == 'Knuckle Curve' ~ 'Curveball',
    pitch_name == 'Slow Curve' ~ 'Curveball',
    pitch_name == 'Slurve' ~ 'Curveball',
    pitch_name == 'Split-Finger' ~ 'Splitter',
    pitch_name == 'Forkball' ~ 'Forkball',
    pitch_name == '4-Seam Fastball' ~ 'Fastball',
    .default = pitch_name
  ))

ui <- navbarPage(
  
  theme = shinytheme("flatly"),
  
  tabPanel("Pitchers",
           
           sidebarLayout(
             
             sidebarPanel(
               
               
               
               selectInput("PitcherTeam", label = "Team",
                           
                           choices = levels(as.factor(data$pitcher_team))),
               
               selectInput("Pitcher", label = "Pitcher",
                           
                           choices = levels(as.factor(data$player_name))),
               
               dateRangeInput("Date", label = "Date Range",
                              start = min(data$game_date),
                              end = max(data$game_date),
                              min = min(data$game_date),
                              max = max(data$game_date),
                              format = "yyyy-mm-dd",
                              separator = "to"),
               
               checkboxGroupInput("Pitch", label = "Pitch Type(s)",
                                  
                                  choices = levels(as.factor(data$pitch_name)),
                                  
                                  selected = levels(as.factor(data$pitch_name))),
               
               radioButtons("PlotChoice", label = "Visible Plot",
                            
                            selected = 'pitches',
                            
                            choiceNames = c("Pitches", "Heat Map", "Zones"),
                            
                            choiceValues = c('pitches', 'heatmap', 'zones')),
               
               width = 5),
             
             mainPanel(
               
               fluidRow(plotOutput("Strike_Zone"))
               
             )),
           
  )
)
  
  server = function(input, output, session) {
    
    # Input Reactions -- Pitcher Tab
    
    
    # Pitchers Based on PitcherTeam    
    
    observeEvent(
      input$PitcherTeam,
      updateSelectInput(session,
                        "Pitcher", "Pitcher",
                        choices = levels(factor(filter(data,
                                                       pitcher_team == isolate(input$PitcherTeam))$player_name))))
    
    
    # Date Range Based on When Pitcher Threw
    
    observeEvent(
      input$Pitcher,
      updateDateRangeInput(session,
                           "Date", "Date Range",
                           start = min(data$game_date),
                           end = max(data$game_date)))
    
    
    # Pitch Types Based on Pitcher
    
    observeEvent(
      input$Pitcher,
      updateCheckboxGroupInput(session,
                               "Pitch", "Pitch Type(s)",
                               choices = levels(factor(filter(data,
                                                              player_name == isolate(input$Pitcher))$pitch_name)),
                               selected = levels(factor(filter(data,
                                                              player_name == isolate(input$Pitcher))$pitch_name))))
    
    # Start of Outputs (Plots and Data Tables)
    
    # Strike_Zone
    
    output$Strike_Zone <- renderPlot({
      
      left <- -8.5/12
      right <- 8.5/12
      bottom <- 18.29/12
      top <- 44.08/12
      
      width <- (right - left)/3
      height <- (top - bottom)/3
      
      data <- data %>%
        filter(pitcher_team == input$PitcherTeam,
               player_name == input$Pitcher,
               pitch_name %in% input$Pitch, 
               c(game_date >= input$Date[1] & game_date <= input$Date[2]))
      
      data <- data %>%
        mutate(zone = case_when(
          ((plate_x >= left) & (plate_x <= (left + width)) & (plate_z <= top) & (plate_z >= (top - height))) ~ 'one',
          ((plate_x >= (left + width)) & (plate_x <= (right - width)) & (plate_z <= top) & (plate_z >= (top - height))) ~ 'two',
          ((plate_x >= (right - width)) & (plate_x <= right) & (plate_z <= top) & (plate_z >= (top - height))) ~ 'three',
          ((plate_x >= left) & (plate_x <= (left + width)) & (plate_z <= (top - height)) & (plate_z >= (bottom + height))) ~ 'four',
          ((plate_x >= (left + width)) & (plate_x <= (right - width)) & (plate_z <= (top - height)) & (plate_z >= (bottom + height))) ~ 'five',
          ((plate_x >= (right - width)) & (plate_x <= right) & (plate_z <= (top - height)) & (plate_z >= (bottom + height))) ~ 'six',
          ((plate_x >= left) & (plate_x <= (left + width)) & (plate_z <= (bottom + height)) & (plate_z >= bottom)) ~ 'seven',
          ((plate_x >= (left + width)) & (plate_x <= (right - width)) & (plate_z <= (bottom + height)) & (plate_z >= bottom)) ~ 'eight',
          ((plate_x >= (right - width)) & (plate_x <= right) & (plate_z <= (bottom + height)) & (plate_z >= bottom)) ~ 'nine',
          .default = 'zero'
        ))
      
      zone_count <- data %>%
        group_by(zone) %>%
        tally()
      
      zone_count <- zone_count %>%
        mutate(pct = n / sum(zone_count$n))
      
      if (!('one' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'one', n = 0, pct = 0)
      }
      if (!('two' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'two', n = 0, pct = 0)
      }
      if (!('three' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'three', n = 0, pct = 0)
      }
      if (!('four' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'four', n = 0, pct = 0)
      }
      if (!('five' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'five', n = 0, pct = 0)
      }
      if (!('six' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'six', n = 0, pct = 0)
      }
      if (!('seven' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'seven', n = 0, pct = 0)
      }
      if (!('eight' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'eight', n = 0, pct = 0)
      }
      if (!('nine' %in% zone_count$zone)) {
        zone_count <- zone_count %>% add_row(zone = 'nine', n = 0, pct = 0)
      }
      
      # print(zone_count)
      
      if (input$PlotChoice == 'heatmap') {
        # Creates A Color Palette, Reversed (Blue/Less Frequent to Red/More Frequent) With 16 Different Shades
        heat_colors_interpolated <- colorRampPalette(paletteer::paletteer_d("RColorBrewer::RdBu", n = 9, direction = -1))(16)
        
        # Shows The Color Scale
        heat_colors_interpolated %>% scales::show_col()
        
        ggplot(data, mapping = aes(x=plate_x, y= plate_z)) +
          stat_density2d_filled()  +
          scale_fill_manual(values = c(heat_colors_interpolated), aesthetics = c("fill", "color")) +
          geom_segment(x = left, y = top, xend = right, yend = top) +
          geom_segment(x = left, y = bottom, xend = right, yend = bottom) +
          geom_segment(x = left, y = top, xend = left, yend = bottom) +
          geom_segment(x = right, y = top, xend = right, yend = bottom) +
          
          geom_segment(x = left, y = (bottom + height), xend = right, yend = (bottom + height)) +
          geom_segment(x = left, y = (top - height), xend = right, yend = (top - height)) +
          geom_segment(x = (left + width), y = bottom, xend = (left + width), yend = top) +
          geom_segment(x = (right - width), y = bottom, xend = (right - width), yend = top) +
          
          geom_segment(x = left, y = 0, xend = right, yend = 0) +
          geom_segment(x = left, y = 0, xend = left, yend = (4.25/12)) +
          geom_segment(x = left, y = (4.25/12), xend = 0, yend = (8.5/12)) +
          geom_segment(x = right, y = (4.25/12), xend = right, yend = 0) +
          geom_segment(x = 0, y = (8.5/12), xend = right, yend = (4.25/12)) +
          theme(plot.title = element_text(hjust = 0.5),
                panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                panel.background = element_blank(),
                legend.position = "none") + 
          xlim(-2.5,2.5) + ylim(-.5, 5) + ggtitle("Strike Zone")
      }
      
      else if (input$PlotChoice == 'zones') {
        
        ggplot(data, mapping = aes(x=plate_x, y=plate_z)) +
          geom_segment(x = left, y = top, xend = right, yend = top) +
          geom_segment(x = left, y = bottom, xend = right, yend = bottom) +
          geom_segment(x = left, y = top, xend = left, yend = bottom) +
          geom_segment(x = right, y = top, xend = right, yend = bottom) +
          
          geom_segment(x = left, y = (bottom + height), xend = right, yend = (bottom + height)) +
          geom_segment(x = left, y = (top - height), xend = right, yend = (top - height)) +
          geom_segment(x = (left + width), y = bottom, xend = (left + width), yend = top) +
          geom_segment(x = (right - width), y = bottom, xend = (right - width), yend = top) +
          
          geom_segment(x = left, y = 0, xend = right, yend = 0) +
          geom_segment(x = left, y = 0, xend = left, yend = (4.25/12)) +
          geom_segment(x = left, y = (4.25/12), xend = 0, yend = (8.5/12)) +
          geom_segment(x = right, y = (4.25/12), xend = right, yend = 0) +
          geom_segment(x = 0, y = (8.5/12), xend = right, yend = (4.25/12)) +
        
          geom_rect(mapping = aes(xmin = left, xmax = (left + width), ymin = (top - height), ymax = top, fill = (filter(zone_count, zone == 'one') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = (left + width), xmax = (right - width), ymin = (top - height), ymax = top, fill = (filter(zone_count, zone == 'two') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = (right - width), xmax = right, ymin = (top - height), ymax = top, fill = (filter(zone_count, zone == 'three') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = left, xmax = (left + width), ymin = (bottom + height), ymax = (top - height), fill = (filter(zone_count, zone == 'four') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = (left + width), xmax = (right - width), ymin = (bottom + height), ymax = (top - height), fill = (filter(zone_count, zone == 'five') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = (right - width), xmax = right, ymin = (bottom + height), ymax = (top - height), fill = (filter(zone_count, zone == 'six') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = left, xmax = (left + width), ymin = bottom, ymax = (bottom + height), fill = (filter(zone_count, zone == 'seven') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = (left + width), xmax = (right - width), ymin = bottom, ymax = (bottom + height), fill = (filter(zone_count, zone == 'eight') %>% pull(pct)))) +
          geom_rect(mapping = aes(xmin = (right - width), xmax = right, ymin = bottom, ymax = (bottom + height), fill = (filter(zone_count, zone == 'nine') %>% pull(pct)))) +
          scale_colour_gradient2(low = 'blue', mid = 'white', high = 'red', midpoint = 0.11, limits = c(0, 1)) +
          theme(plot.title = element_text(hjust = 0.5),
                panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                panel.background = element_blank(),
                legend.position = "none") + 
          xlim(-2.5,2.5) + ylim(-.5, 5) + ggtitle("Strike Zone")
          
      }
      
      else {
        ggplot(data, mapping = aes(x=plate_x, y= plate_z)) +
          geom_point(aes(color = pitch_name),size = 3, alpha=0.5) +
          scale_color_manual(values = c(Changeup = "blue", Fastball = "black",
                                        Slider = "orange", Curveball = "red",
                                        Cutter = "green",Sinker = "brown",
                                        Splitter = "purple", Knuckleball = "cyan", Forkball = "pink", Sweeper = "gold"))+
          geom_segment(x = left, y = top, xend = right, yend = top) +
          geom_segment(x = left, y = bottom, xend = right, yend = bottom) +
          geom_segment(x = left, y = top, xend = left, yend = bottom) +
          geom_segment(x = right, y = top, xend = right, yend = bottom) +
          
          geom_segment(x = left, y = (bottom + height), xend = right, yend = (bottom + height)) +
          geom_segment(x = left, y = (top - height), xend = right, yend = (top - height)) +
          geom_segment(x = (left + width), y = bottom, xend = (left + width), yend = top) +
          geom_segment(x = (right - width), y = bottom, xend = (right - width), yend = top) +
          
          geom_segment(x = left, y = 0, xend = right, yend = 0) +
          geom_segment(x = left, y = 0, xend = left, yend = (4.25/12)) +
          geom_segment(x = left, y = (4.25/12), xend = 0, yend = (8.5/12)) +
          geom_segment(x = right, y = (4.25/12), xend = right, yend = 0) +
          geom_segment(x = 0, y = (8.5/12), xend = right, yend = (4.25/12)) +
          theme(plot.title = element_text(hjust = 0.5),
                panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                panel.background = element_blank(),
                legend.position = "none") + 
          xlim(-2.5,2.5) + ylim(-.5, 5) + ggtitle("Strike Zone")
      }
      
      
      
    })
    
  }
  
shinyApp(ui = ui, server = server)
