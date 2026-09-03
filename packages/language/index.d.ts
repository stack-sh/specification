export interface TextMateCapture {
  readonly name?: string;
  readonly patterns?: readonly TextMateRule[];
}

export interface TextMateRule {
  readonly name?: string;
  readonly match?: string;
  readonly begin?: string;
  readonly end?: string;
  readonly include?: string;
  readonly beginCaptures?: Readonly<Record<string, TextMateCapture>>;
  readonly endCaptures?: Readonly<Record<string, TextMateCapture>>;
  readonly patterns?: readonly TextMateRule[];
}

export interface StackLanguageGrammar {
  readonly $schema?: string;
  readonly name: "stack";
  readonly scopeName: "source.stack";
  readonly fileTypes: readonly ["stack"];
  readonly patterns: readonly TextMateRule[];
  readonly repository: Readonly<Record<string, TextMateRule>>;
}

export interface LanguagePair {
  readonly open: string;
  readonly close: string;
  readonly notIn?: readonly string[];
}

export interface StackLanguageConfiguration {
  readonly comments: {
    readonly lineComment: "//";
  };
  readonly brackets: readonly (readonly [string, string])[];
  readonly autoClosingPairs: readonly LanguagePair[];
  readonly surroundingPairs: readonly (readonly [string, string])[];
  readonly wordPattern: string;
}

export declare const stackLanguage: StackLanguageGrammar;
export declare const languageConfiguration: StackLanguageConfiguration;

export default stackLanguage;
