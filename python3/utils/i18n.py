import json
import locale
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional


class I18n:
    """Internationalization utility class."""

    _DEFAULT_LANGUAGE = 'en'
    _translations: Dict[str, Dict[str, Any]] = {}
    _current_language: str = None
    _fallback_language: str = None
    _locales_dir: Path = None
    _logger: logging.Logger = None

    @staticmethod
    def init_i18n(locales_dir: Path, language: Optional[str] = None, fallback_language: Optional[str] = None, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the i18n system by loading the specified language and fallback language.

        Args:
            locales_dir: Path to the directory containing JSON translation files
            language: Language code to load (e.g., 'es', 'en'). If None, detects system language.
            fallback_language: Fallback language code to use when translations are missing. Defaults to 'en'.
            logger: Logger instance for warnings. If None, creates a basic console logger.

        Raises:
            FileNotFoundError: If locales directory or language files don't exist
            ValueError: If JSON files have invalid format
        """
        I18n._locales_dir = Path(locales_dir)

        if not I18n._locales_dir.exists():
            raise FileNotFoundError(f"Locales directory not found: {I18n._locales_dir}")

        # Setup logger
        if logger is None:
            I18n._logger = logging.getLogger()
            # Configure basic format only if not already configured
            if not I18n._logger.handlers:
                logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)
        else:
            I18n._logger = logger

        # Auto-detect system language if not specified
        if language is None:
            language = I18n.get_system_language()

        # Use default fallback language if not specified
        if fallback_language is None:
            fallback_language = I18n._DEFAULT_LANGUAGE

        I18n._configure_languages(language, fallback_language)

    @staticmethod
    def set_language(language: str, fallback_language: str) -> None:
        """
        Reconfigure the i18n system with new language and fallback language.

        Args:
            language: Language code to load (e.g., 'es', 'en')
            fallback_language: Fallback language code to use when translations are missing

        Raises:
            RuntimeError: If i18n system hasn't been initialized
            FileNotFoundError: If language files don't exist
            ValueError: If JSON files have invalid format
        """
        if I18n._locales_dir is None:
            raise RuntimeError("I18n system not initialized. Call init_i18n() first.")

        I18n._configure_languages(language, fallback_language)

    @staticmethod
    def t(key: str) -> str:
        """
        Get translation for the specified key.

        Looks up the key in the current language first, then falls back to the
        fallback language if not found. If the key doesn't exist in either language,
        returns the key itself and logs a warning.

        Args:
            key: Translation key to look up

        Returns:
            The translated string, or the key itself if not found
        """
        # Try current language
        if I18n._current_language and key in I18n._translations.get(I18n._current_language, {}):
            return I18n._translations[I18n._current_language][key]

        # Try fallback language
        if I18n._fallback_language and key in I18n._translations.get(I18n._fallback_language, {}):
            I18n._logger.warning(f"Translation key '{key}' not found in '{I18n._current_language}', using fallback '{I18n._fallback_language}'")
            return I18n._translations[I18n._fallback_language][key]

        # Key not found in any language
        I18n._logger.warning(f"Translation key not found in any language: '{key}'")
        return key

    @staticmethod
    def get_available_languages() -> List[str]:
        """
        Get a list of all available language codes.

        Returns:
            List of language codes (e.g., ['es', 'en'])

        Raises:
            RuntimeError: If i18n system hasn't been initialized
        """
        if I18n._locales_dir is None:
            raise RuntimeError("I18n system not initialized. Call init_i18n() first.")

        return [file.stem for file in I18n._locales_dir.glob("*.json")]

    @staticmethod
    def get_system_language() -> str:
        """
        Get the system's default language code.

        Returns:
            System language code (e.g., 'es', 'en'), or default language if detection fails
        """
        try:
            lang = locale.getlocale()[0]
            if lang:
                return lang.split('_')[0]
        except Exception:
            pass
        return I18n._DEFAULT_LANGUAGE

    @staticmethod
    def _configure_languages(language: str, fallback_language: str) -> None:
        """
        Load and configure the specified languages.

        Args:
            language: Language code to load (e.g., 'es', 'en')
            fallback_language: Fallback language code to use when translations are missing

        Raises:
            FileNotFoundError: If language files don't exist
            ValueError: If JSON files have invalid format
        """
        # Load both languages (only if not already loaded)
        if language not in I18n._translations:
            I18n._load_language(language)
        if fallback_language not in I18n._translations:
            I18n._load_language(fallback_language)

        # Set current and fallback languages
        I18n._current_language = language
        I18n._fallback_language = fallback_language

    @staticmethod
    def _load_language(language_code: str) -> None:
        """
        Load a specific language file.

        Args:
            language_code: Language code (e.g., 'es', 'en')

        Raises:
            FileNotFoundError: If the language file doesn't exist
            ValueError: If the JSON file has invalid format
        """
        language_file = I18n._locales_dir / f"{language_code}.json"

        if not language_file.exists():
            raise FileNotFoundError(f"Language file not found: {language_file}")

        try:
            with open(language_file, 'r', encoding='utf-8') as f:
                I18n._translations[language_code] = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {language_file}: {e}")


if __name__ == '__main__':
    # Example usage
    from pathlib import Path

    # Get the locales directory (python3/assets/locales/)
    locales_dir = Path(__file__).parent.parent / 'assets' / 'locales'

    # Initialize i18n with auto-detected language
    I18n.init_i18n(locales_dir)

    print(f"Current language: {I18n._current_language}")
    print(f"Fallback language: {I18n._fallback_language}")
    print(f"Available languages: {I18n.get_available_languages()}")

    # Test translations
    print(f"Test translation: {I18n.t('test_key')}")

    # Test with different languages
    print("\n--- Testing different languages ---")
    for lang in I18n.get_available_languages():
        I18n.set_language(lang, 'en')
        print(f"{lang}: {I18n.t('test_key')}")
