from statistics import mean


def generate_insights_text(data: list[dict]) -> str:
    """
    data: lista de dicts vindos do serializer do WeatherLog.
    Aqui fazemos uma análise bem simplificada.
    """
    if not data:
        return "Ainda não há dados suficientes para gerar insights climáticos."

    temps = [d['temperature'] for d in data if d['temperature'] is not None]
    hums = [d['humidity'] for d in data if d['humidity'] is not None]
    rains = [d['rain_probability'] for d in data if d['rain_probability'] is not None] # noqa E501

    insights = []

    if temps:
        avg_temp = round(mean(temps), 1)
        max_temp = round(max(temps), 1)
        min_temp = round(min(temps), 1)
        insights.append(
            f"A temperatura média no período foi de {avg_temp}°C, "
            f"com máxima de {max_temp}°C e mínima de {min_temp}°C."
        )

        if avg_temp >= 30:
            insights.append("O período foi predominantemente quente; considere reforçar cuidados com hidratação.") # noqa E501
        elif avg_temp <= 18:
            insights.append("As temperaturas foram mais amenas/fria; atenção a possíveis frentes frias.") # noqa E501

    if hums:
        avg_hum = round(mean(hums), 1)
        insights.append(
            f"A umidade relativa do ar média ficou em torno de {avg_hum}%."
        )
        if avg_hum < 40:
            insights.append("A umidade baixa pode causar desconforto respiratório, recomenda-se uso de umidificadores.") # noqa E501
        elif avg_hum > 80:
            insights.append("Umidade elevada, aumentando a sensação de abafamento e a chance de mofo em ambientes fechados.") # noqa E501

    if rains:
        avg_rain = round(mean(rains), 1)
        insights.append(
            f"A probabilidade média de chuva foi de {avg_rain}% no período."
        )
        if avg_rain > 60:
            insights.append("Há forte tendência de chuvas; planeje atividades externas com cautela.") # noqa E501 
        elif avg_rain < 20:
            insights.append("Baixa probabilidade de chuva, período relativamente seco.") # noqa E501

    if not insights:
        return "Os dados disponíveis ainda são limitados para conclusões mais detalhadas." # noqa E501

    return " ".join(insights)
