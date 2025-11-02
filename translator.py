import re
import time
import requests
from pathlib import Path

class SmartTranslator:
    def __init__(self):
        self.session = requests.Session()
        self.translated_count = 0
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        })
        
    def translate_google(self, text, target_lang="ru"):
        """Google Translate API"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data[0][0][0]
            return text
        except:
            return text

    def translate_snbt_file(self, file_path, target_lang="ru"):
        """Улучшенный перевод SNBT файла"""
        print(f"🧠 ПЕРЕВОД ФАЙЛА: {file_path.name}")
        print("=" * 50)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Улучшенное регулярное выражение для текстов в кавычках
        text_pattern = r'(")([^"\n]+)(")'
        matches = list(re.finditer(text_pattern, content))
        
        print(f"📊 Найдено текстовых блоков: {len(matches)}")
        print("🔄 Начинаю перевод...")
        print()
        
        translated_count = 0
        skipped_count = 0
        
        for i, match in enumerate(matches):
            original_text = match.group(2).strip()
            
            # Улучшенная фильтрация
            if (len(original_text) < 2 or 
                original_text.startswith('{') or
                original_text.startswith('[') or
                original_text.startswith(']') or
                'quest.' in original_text or
                'minecraft:' in original_text or
                re.match(r'^[a-f0-9-]{36}$', original_text) or  # UUID
                re.match(r'^[0-9a-fA-F]{8}-', original_text) or  # UUID pattern
                ':' in original_text and len(original_text) < 15):
                skipped_count += 1
                continue
            
            # Показываем прогресс каждые 20 текстов
            if i % 20 == 0:
                print(f"📈 Обработано: {i}/{len(matches)}, Переведено: {translated_count}")
            
            print(f"   [{i+1}] Исходный: {original_text[:60]}...")
            
            # Переводим
            translated_text = self.translate_google(original_text, target_lang)
            
            if translated_text != original_text:
                # Заменяем в содержимом
                new_content = match.group(1) + translated_text + match.group(3)
                content = content.replace(match.group(0), new_content)
                translated_count += 1
                print(f"      ✅ Перевод: {translated_text[:60]}...")
            else:
                print(f"      ⏩ Пропуск (перевод не изменился)")
                skipped_count += 1
            
            # Пауза чтобы не блокировать API
            if i % 10 == 0:
                time.sleep(0.3)
        
        # Сохраняем результат
        output_file = file_path.parent / f"{file_path.stem}_TRANSLATED_RU{file_path.suffix}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 ПЕРЕВОД ЗАВЕРШЕН!")
        print(f"✅ Успешно переведено: {translated_count} элементов")
        print(f"⏩ Пропущено: {skipped_count} технических элементов")
        print(f"💾 Файл сохранен: {output_file.name}")
        return output_file

def main():
    print("🚀 ПЕРЕВОДЧИК ДЛЯ MINECRAFT")
    print("=" * 50)
    
    translator = SmartTranslator()
    
    # Путь к файлу
    file_path = input("Введите путь к en_us.snbt: ").strip()
    
    if not file_path:
        # Автопоиск стандартных путей
        possible_paths = [
            r"C:\Users\nikit\AppData\Roaming\.minecraft\config\ftbquests\quests\lang\en_us.snbt",
            r"config\ftbquests\quests\lang\en_us.snbt",
            r"\.minecraft\config\ftbquests\quests\lang\en_us.snbt",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                file_path = path
                break
        else:
            print("❌ Файл не найден! Укажите путь вручную.")
            return
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        return
    
    print(f"📁 Найден файл: {file_path}")
    print(f"🎯 Начинаю перевод...")
    
    start_time = time.time()
    output_file = translator.translate_snbt_file(file_path)
    end_time = time.time()
    
    print(f"⏱️ Время выполнения: {end_time - start_time:.1f} секунд")
    
    print(f"\n🚀 ИНСТРУКЦИЯ ПО АКТИВАЦИИ:")
    print(f'1. Переименуй файл: "{output_file.name}" → "ru_ru.snbt"')
    print(f'2. Замени старый файл ru_ru.snbt в папке: {file_path.parent}')
    print("3. Перезапусти Minecraft")
    print("\n🎮 Приятной игры!")

if __name__ == "__main__":
    main()