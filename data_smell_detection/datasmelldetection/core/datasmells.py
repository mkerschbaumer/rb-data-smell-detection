from enum import Enum


class DataSmellType(Enum):
    """An enum which contains the data smells which detectors can find in datasets."""

    DUMMY_VALUE_SMELL = "Dummy Value Smell"
    """
    This smell characterizes a situation in which a kind of substitute value (sentinel value) is
    used due to several reasons (e.g. missing values, unknown values, computation errors, surpass
    'not NULL' constraints etc.).
    """  # pylint: disable=W0105

    DUPLICATED_VALUE_SMELL = "Duplicated Value Smell"
    """
    This smell occurs when data values are syntactically equal across several data instances.
    """  # pylint: disable=W0105

    EXTREME_VALUE_SMELL = "Extreme Value Smell"
    """
    This smell occurs when data instances have extreme data values relating to other data instances.
    """  # pylint: disable=W0105

    MEANINGLESS_VALUE_SMELL = "Meaningless Value Smell"
    """
    This smell arises when a data value has no common meaning or contains suspect repeating
    sequences of characters.
    """  # pylint: disable=W0105

    MISSPELLING_SMELL = "Misspelling Smell"
    """
    This smell arises when a data value probably has a spelling error.
    """  # pylint: disable=W0105

    SUSPECT_CLASS_VALUE_SMELL = "Suspect Class Value Smell"
    """
    This smell characterizes a situation in which categorical data instances have uncommon class
    values.
    """  # pylint: disable=W0105

    SUSPECT_DATE_VALUE_SMELL = "Suspect Date Value Smell"
    """
    This smell occurs when a data value represents a date far in the past or future.
    """  # pylint: disable=W0105

    SUSPECT_DATE_TIME_INTERVAL_SMELL = "Suspect Date/Time Interval Smell"
    """
    This smell occurs when there is a very long/short date/time interval between data instances.
    """  # pylint: disable=W0105

    SUSPECT_SIGN_SMELL = "Suspect Sign Smell"
    """
    This smell occurs when data instances have a different sign (+/-) than the rest of the
    instances.
    """  # pylint: disable=W0105

    SUSPECT_DISTRIBUTION_SMELL = "Suspect Distribution Smell"
    """
    This smell characterizes a situation in which the data values have a suspect distribution.
    """  # pylint: disable=W0105

    AMBIGUOUS_DATE_TIME_FORMAT_SMELL = "Ambiguous Date/Time Format Smell"
    """
    This smell occurs when a date is represented in short format or a timestamp is represented in 12
    hour format.
    """  # pylint: disable=W0105

    AMBIGUOUS_VALUE_SMELL = "Ambiguous Value Smell"
    """
    This smell arises when data values represent abbreviations, homonyms, acronyms or an ambiguous
    context.
    """  # pylint: disable=W0105

    CASING_SMELL = "Casing Smell"
    """
    This smell occurs when data values represent an unusual use of upper and lower case (Mixed Case,
    Upper Only, Lower Only).
    """  # pylint: disable=W0105

    CONTRACTING_SMELL = "Contracting Smell"
    """
    This smell occurs when data values represent shortened version of words or phrases.
    """  # pylint: disable=W0105

    EXTRANEOUS_VALUE_SMELL = "Extraneous Value Smell"
    """
    This smell occurs when data values provide additional, likely unnecessary information.
    """  # pylint: disable=W0105

    INTERMINGLED_DATA_TYPE_SMELL = "Intermingled Data Type Smell"
    """
    This smell characterizes a situation in which data values contain numeric and alphabetic
    characters.
    """  # pylint: disable=W0105

    LONG_DATA_VALUE_SMELL = "Long Data Value Smell"
    """This smell arises when data values are too long to understand."""  # pylint: disable=W0105

    MISSING_VALUE_SMELL = "Missing Value Smell"
    """This smell arises when data instances have no data values."""  # pylint: disable=W0105

    SEPARATING_SMELL = "Separating Smell"
    """
    This smell arises when data values contain thousands separators (space, underbar, dot etc.) for
    grouping digits. The usage of delimiters can result in ambiguity when also a decimal separator
    is used and lead to problems decoding the values.
    """  # pylint: disable=W0105

    SPACING_SMELL = "Spacing Smell"
    """
    This smell arises when data values contain an uncommon pattern of spaces (Trailing Space,
    Leading Spaces, Multiple Spaces, Missing Spaces).
    """  # pylint: disable=W0105

    SPECIAL_CHARACTER_SMELL = "Special Character Smell"
    """
    This smell occurs when data values contain special characters (non-alphanumeric) like Commas,
    Dots, Hyphens, Apostrophes, Tab Char, Punctuation, Parentheses, Dashes, accented Letters, etc.
    """  # pylint: disable=W0105

    SYNONYM_SMELL = "Synonym Smell"
    """
    This smell occurs when data values have the same semantic meaning but are syntactically
    different (e.g. Aliases, Nick names, Pseudonyms).
    """  # pylint: disable=W0105

    TAGGING_SMELL = "Tagging Smell"
    """This smell occurs when data values represent tags."""  # pylint: disable=W0105

    DATE_AS_DATE_TIME_SMELL = "Date As DateTime Smell"
    """
    This smell occurs when a date is encoded as a datetime data type.
    """  # pylint: disable=W0105

    DATE_AS_STRING_SMELL = "Date As String Smell"
    """This smell occurs when a date is encoded as a string."""  # pylint: disable=W0105

    DATE_TIME_AS_STRING_SMELL = "DateTime As String Smell"
    """
    This smell occurs when a date and a timestamp are encoded as a string.
    """  # pylint: disable=W0105

    FLOATING_POINT_NUMBER_AS_STRING_SMELL = "Floating Point Number As String Smell"
    """
    This smell occurs when a floating-point number is encoded as a string.
    """  # pylint: disable=W0105

    INTEGER_AS_FLOATING_POINT_NUMBER_SMELL = "Integer As Floating Point Number Smell"
    """
    This smell occurs when an integer is encoded as a floating-point number.
    """  # pylint: disable=W0105

    INTEGER_AS_STRING_SMELL = "Integer As String Smell"
    """This smell occurs when an integer is encoded as a string."""  # pylint: disable=W0105

    TIME_AS_STRING_SMELL = "Time As String Smell"
    """This smell occurs when a timestamp is encoded as a string."""  # pylint: disable=W0105

    SUSPECT_CHARACTER_ENCODING_SMELL = "Suspect Character Encoding Smell"
    """
    This smells occurs when special characters or umlauts are incorrectly encoded.
    """  # pylint: disable=W0105

    ABBREVIATION_INCONSISTENCY_SMELL = "Abbreviation Inconsistency Smell"
    """
    This smell occurs when abbreviations or contractions are not used consistently.
    """  # pylint: disable=W0105

    CASING_INCONSISTENCY_SMELL = "Casing Inconsistency Smell"
    """
    This smell characterizes a situation in which upper and lower case is not used consistently.
    """  # pylint: disable=W0105

    CLASS_INCONSISTENCY_SMELL = "Class Inconsistency Smell"
    """
    This smell arises when class values for categorical data instances are not used consistently
    (e.g. different representations or abstractions).
    """  # pylint: disable=W0105

    DATE_TIME_FORMAT_INCONSISTENCY_SMELL = "Date/Time Format Inconsistency Smell"
    """
    This smell occurs when date or time formats are not used consistently.
    """  # pylint: disable=W0105

    MISSING_VALUE_INCONSISTENCY_SMELL = "Missing Value Inconsistency Smell"
    """
    This smell characterizes a situation in which constants are not used consistently to represent
    missing data values.
    """  # pylint: disable=W0105

    SEPARATING_INCONSISTENCY_SMELL = "Separating Inconsistency Smell"
    """
    This smell occurs when thousands separator are not used consistently.
    """  # pylint: disable=W0105

    SPACING_INCONSISTENCY_SMELL = "Spacing Inconsistency Smell"
    """This smell occurs when spacing is not used consistenly."""  # pylint: disable=W0105

    SPECIAL_CHARACTER_INCONSISTENCY_SMELL = "Special Character Inconsistency Smell"
    """
    This smell occurs when special characters are not used consistently.
    """  # pylint: disable=W0105

    SYNTAX_INCONSISTENCY_SMELL = "Syntax Inconsistency Smell"
    """
    This smell characterizes a situation in which the general syntax (decimal places, telephone area
    codes, extraneous information etc.) of data values is not used consistently. Mainly, all other
    consistency issues which do not fall in one of the other categories related to this category.
    """  # pylint: disable=W0105

    UNIT_INCONSISTENCY_SMELL = "Unit Inconsistency Smell"
    """
    This smell arises when units of measurement are not (implicitly) used consistently.
    """  # pylint: disable=W0105

    TRANSPOSITION_INCONSISTENCY_SMELL = "Transposition Inconsistency Smell"
    """
    This smell arises when ordering of words or special characters is not used consistently.
    """  # pylint: disable=W0105
