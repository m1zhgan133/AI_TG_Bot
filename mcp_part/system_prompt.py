import datetime

# Создаем системный промпт с инструкциями
system_prompt = f"""
    [System Instructions]
    Current datetime: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    General rules:
    - Always check current date before answering time-sensitive questions
   """