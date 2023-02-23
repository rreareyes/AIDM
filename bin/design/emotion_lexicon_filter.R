library(tidyverse)

anger_words <- lexicon::nrc_emotions %>% 
  filter(anger == 1)

fear_words <- lexicon::nrc_emotions %>% 
  filter(fear == 1)

write_csv(x    = anger_words, 
          file = "anger_lexicon_nrc.csv")

write_csv(x    = fear_words, 
          file = "fear_lexicon_nrc.csv")
