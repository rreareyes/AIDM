generate_deck <- function(fixed_ev, n_cards){
  
  initial_data = tibble(draw       = 1:(n_cards),
                        cards_left = n_cards - lag(draw, default = 0),
                        p_lose     = 1/(n_cards - lag(draw, default = 0)),
                        p_win      = 1 - p_lose,
                        bank_value = 0,
                        reward     = 0)
  
  initial_data$reward[1] = fixed_ev/initial_data$p_win[1]
  
  for (iDraw in 2:length(initial_data$draw)) {
    
    initial_data$bank_value[iDraw] = lag(initial_data$bank_value, default = 0)[iDraw] + lag(initial_data$reward, default = 0)[iDraw]
    initial_data$reward[iDraw]     = (fixed_ev + (initial_data$bank_value[iDraw] * initial_data$p_lose[iDraw])) / initial_data$p_win[iDraw]
    
  }
  
  deck_data = initial_data |> 
    mutate(ev_win  = p_win * reward,
           ev_lose = p_lose * bank_value,
           ev_draw = ev_win - ev_lose,
           rw_round   = plyr::round_any(reward, 0.5),
           bn_rd      = lag(cumsum(rw_round), default = 0),
           ev_win_rd  = rw_round * p_win,
           ev_lose_rd = bn_rd * p_lose,
           ev_rd      = ev_win_rd - ev_lose_rd)
  
  return(deck_data)
}
