import stackLanguage, {
  languageConfiguration,
  type StackLanguageConfiguration,
  type StackLanguageGrammar,
} from "@stack-sh/language";
import rawGrammar from "@stack-sh/language/grammar";
import rawLanguageConfiguration from "@stack-sh/language/language-configuration";

const grammar: StackLanguageGrammar = stackLanguage;
const configuration: StackLanguageConfiguration = languageConfiguration;
const scopeName: "source.stack" = rawGrammar.scopeName;
const lineComment: "//" = rawLanguageConfiguration.comments.lineComment;

void grammar;
void configuration;
void scopeName;
void lineComment;
