import pandas as pd
import numpy as np
from scipy.stats import poisson

class FootballBettingEngine:
    def __init__(self):
        # Competizioni supportate (Campionati + Coppe Europee)
        self.competitions = {
            "Serie A (Italia)": "IT1",
            "Premier League (Inghilterra)": "ENG1",
            "La Liga (Spagna)": "SP1",
            "Bundesliga (Germania)": "GER1",
            "Ligue 1 (Francia)": "FR1",
            "Champions League (Europa)": "UCL",
            "Europa League / Conference (Europa)": "UEL"
        }
        
    def get_supported_competitions(self):
        return list(self.competitions.keys())

    def get_calendar_matches(self, competition_name):
        """
        Restituisce un calendario di partite per la competizione selezionata,
        includendo le giornate e le squadre di casa e trasferta.
        """
        calendar_data = {
            "Serie A (Italia)": [
                {"Giornata": "12ª Giornata", "Data": "10 Nov 2026 - 15:00", "Casa": "Venezia", "Trasferta": "Udinese"},
                {"Giornata": "12ª Giornata", "Data": "10 Nov 2026 - 18:00", "Casa": "Inter", "Trasferta": "Napoli"},
                {"Giornata": "12ª Giornata", "Data": "11 Nov 2026 - 20:45", "Casa": "Juventus", "Trasferta": "Milan"},
                {"Giornata": "13ª Giornata", "Data": "22 Nov 2026 - 15:00", "Casa": "Roma", "Trasferta": "Atalanta"}
            ],
            "Premier League (Inghilterra)": [
                {"Giornata": "11ª Giornata", "Data": "10 Nov 2026 - 16:00", "Casa": "Manchester City", "Trasferta": "Liverpool"},
                {"Giornata": "11ª Giornata", "Data": "10 Nov 2026 - 18:30", "Casa": "Arsenal", "Trasferta": "Chelsea"},
                {"Giornata": "12ª Giornata", "Data": "23 Nov 2026 - 15:00", "Casa": "Tottenham", "Trasferta": "Manchester United"}
            ],
            "La Liga (Spagna)": [
                {"Giornata": "13ª Giornata", "Data": "10 Nov 2026 - 21:00", "Casa": "Real Madrid", "Trasferta": "Barcelona"},
                {"Giornata": "13ª Giornata", "Data": "11 Nov 2026 - 18:30", "Casa": "Atletico Madrid", "Trasferta": "Girona"}
            ],
            "Champions League (Europa)": [
                {"Giornata": "5ª Giornata (Fase a Gironi)", "Data": "26 Nov 2026 - 21:00", "Casa": "Real Madrid", "Trasferta": "Manchester City"},
                {"Giornata": "5ª Giornata (Fase a Gironi)", "Data": "26 Nov 2026 - 21:00", "Casa": "Bayern München", "Trasferta": "Inter"},
                {"Giornata": "5ª Giornata (Fase a Gironi)", "Data": "27 Nov 2026 - 21:00", "Casa": "Paris Saint-Germain", "Trasferta": "Arsenal"}
            ],
            "Europa League / Conference (Europa)": [
                {"Giornata": "5ª Giornata", "Data": "27 Nov 2026 - 18:45", "Casa": "Roma", "Trasferta": "Bayer Leverkusen"},
                {"Giornata": "5ª Giornata", "Data": "27 Nov 2026 - 21:00", "Casa": "Atalanta", "Trasferta": "Villarreal"}
            ]
        }
        default_matches = [
            {"Giornata": "1ª Giornata", "Data": "15 Nov 2026 - 15:00", "Casa": "Squadra A", "Trasferta": "Squadra B"}
        ]
        return calendar_data.get(competition_name, default_matches)

    def calculate_poisson_1x2(self, lambda_home, lambda_away):
        """Calcola le probabilità 1X2 tramite la distribuzione di Poisson."""
        max_events = 15
        prob_home_win, prob_draw, prob_away_win = 0.0, 0.0, 0.0

        for h in range(max_events + 1):
            for a in range(max_events + 1):
                p = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)
                if h > a:
                    prob_home_win += p
                elif h == a:
                    prob_draw += p
                else:
                    prob_away_win += p

        total = prob_home_win + prob_draw + prob_away_win
        if total > 0:
            prob_home_win /= total
            prob_draw /= total
            prob_away_win /= total

        return {
            "1 (Casa)": round(prob_home_win * 100, 2),
            "X (Pareggio)": round(prob_draw * 100, 2),
            "2 (Trasferta)": round(prob_away_win * 100, 2)
        }

    def get_detailed_match_stats(self, home_team, away_team, filter_campo, filter_avversaria):
        """
        Genera le statistiche avanzate stimate in base ai filtri di contesto 
        (Casa/Trasferta e Tipo di Avversaria: Big, Medie, Piccole)
        """
        modifier = 1.0
        if filter_campo == "Solo in Casa (per Casa) / Fuori (per TRF)":
            modifier = 1.05
        elif filter_campo == "Solo in Trasferta (per Casa) / Casa (per TRF)":
            modifier = 0.95

        stats = {
            "Gol attesi": {"home": 1.37 * modifier, "away": 1.49},
            "Tiri attesi": {"home": 14.4 * modifier, "away": 15.42},
            "Tiri in porta attesi": {"home": 4.9 * modifier, "away": 5.05},
            "Calci d'angolo attesi": {"home": 5.5 * modifier, "away": 5.1},
            "Parate attese": {"home": 3.56, "away": 3.54},
            "Falli commessi attesi": {"home": 9.45, "away": 9.95},
            "Fuorigioco attesi": {"home": 2.71, "away": 1.7},
            "Cartellini attesi": {"home": 1.45, "away": 1.45}
        }

        market_results = {}
        for market, values in stats.items():
            if market != "Gol attesi":
                probs = self.calculate_poisson_1x2(values["home"], values["away"])
                market_results[market] = {
                    "home_val": round(values["home"], 2),
                    "away_val": round(values["away"], 2),
                    "probabilities": probs
                }

        return stats, market_results
