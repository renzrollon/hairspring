# `form-import.csv` format and its limits

`form-import.csv` is a tool-neutral definition of the form, one row per item, so the questionnaire is reviewable in a diff and can be rebuilt in any form tool. Be clear with users about what it is not: **neither Google Forms nor Microsoft Forms imports a CSV of questions natively.** The paths below work around that.

## Columns

```text
ID,Type,Title,HelpText,Required,Options,ScaleMin,ScaleMax,MinLabel,MaxLabel
```

| Column | Values | Rule |
| --- | --- | --- |
| `ID` | `Q01`, `Q02`, ... for questions; `SEC1`, `SEC2`, ... for sections | Matches the *Questions* table in `questionnaire.md` and `Item` in `analysis.csv` |
| `Type` | `section`, `scale`, `single`, `multi`, `dropdown`, `short`, `paragraph` | `single` = one choice (radio buttons), `multi` = checkboxes, `short` = one line of text, `paragraph` = long text |
| `Title` | The question text shown to respondents | Unique across the form: the response export uses it as the column header, and the analysis script matches on it |
| `HelpText` | Short instruction under the question, or the introduction text on a section | Optional |
| `Required` | `yes`, `no` | Optional items allow "don't know" as a blank |
| `Options` | Choices separated by `\|` | For `single`, `multi`, `dropdown`; no `\|` inside an option |
| `ScaleMin`, `ScaleMax` | Integers | For `scale` only. Google Forms allows a lower bound of 0 or 1 and an upper bound of 2 to 10 |
| `MinLabel`, `MaxLabel` | Labels of the two end points | For `scale` only |

The first `section` row gives the form its title and introduction text; later `section` rows start new pages.

## Not supported (by design or by the tools)

- Branching and skip logic, quizzes and scoring, answer validation rules, images, file uploads.
- Grid or matrix questions: use one `scale` row per statement; it also keeps one hypothesis per question.
- Labels on the middle points of a Google Forms linear scale. If every point must be labelled, use `single` with the labels as options, and analyze it with `share:<option>`.

## Google Forms: build the form with Apps Script

1. Create a Google Sheet, import `form-import.csv` (File, Import, replace the current sheet).
2. Open Extensions, Apps Script, paste the script below, save, and run `buildForm`. Grant the permissions it asks for.
3. The execution log prints the edit link of the new form. Check every question against `questionnaire.md` before sending; this script is not run in this repository's CI, so try it on a copy first.

```javascript
// Builds a Google Form from a sheet holding form-import.csv (re-skills questionnaire-builder).
function buildForm() {
  const rows = SpreadsheetApp.getActiveSheet().getDataRange().getValues();
  const header = rows.shift().map(String);
  const get = (row, name) => {
    const i = header.indexOf(name);
    return i < 0 ? '' : String(row[i]).trim();
  };
  const form = FormApp.create('Questionnaire');
  form.setCollectEmail(false);
  let first = true;
  rows.forEach((row) => {
    const type = get(row, 'Type');
    const title = get(row, 'Title');
    const help = get(row, 'HelpText');
    const options = get(row, 'Options').split('|').map((o) => o.trim()).filter(String);
    if (type === 'section') {
      if (first) {
        form.setTitle(title).setDescription(help);
      } else {
        form.addPageBreakItem().setTitle(title).setHelpText(help);
      }
      first = false;
      return;
    }
    first = false;
    let item;
    if (type === 'scale') {
      item = form.addScaleItem()
        .setBounds(Number(get(row, 'ScaleMin')), Number(get(row, 'ScaleMax')))
        .setLabels(get(row, 'MinLabel'), get(row, 'MaxLabel'));
    } else if (type === 'single') {
      item = form.addMultipleChoiceItem().setChoiceValues(options);
    } else if (type === 'multi') {
      item = form.addCheckboxItem().setChoiceValues(options);
    } else if (type === 'dropdown') {
      item = form.addListItem().setChoiceValues(options);
    } else if (type === 'short') {
      item = form.addTextItem();
    } else if (type === 'paragraph') {
      item = form.addParagraphTextItem();
    } else {
      throw new Error('Unknown Type "' + type + '" in row ' + get(row, 'ID'));
    }
    item.setTitle(title).setHelpText(help).setRequired(get(row, 'Required').toLowerCase() === 'yes');
  });
  Logger.log(form.getEditUrl());
}
```

Form add-ons that build forms from a sheet exist too; their column formats differ, so map the columns by hand if you use one.

## Microsoft Forms

- There is no CSV import. Microsoft Forms has a *Quick import* that reads a Word or PDF document and proposes questions; availability depends on the tenant and the account type. To use it, convert `questionnaire.md` to Word (for example `pandoc questionnaire.md -o questionnaire.docx`), import, then check every question: scale items usually arrive as choice questions and need to be changed to *Rating* or *Likert*.
- Otherwise build the form by hand, using `form-import.csv` as the checklist: one row, one question, in order.

## Exporting responses for the analysis script

| Tool | How | Notes |
| --- | --- | --- |
| Google Forms | Responses tab, *Download responses (.csv)* (or open the linked sheet and download it as CSV) | First column is a timestamp; multiple-choice answers are joined with `, ` |
| Microsoft Forms | Responses tab, *Open in Excel*, then save as *CSV UTF-8* | Extra columns (ID, start and completion time, name, email) are ignored; multiple-choice answers are joined with `;` |

The script matches each item to the column whose header equals its `Title` (ignoring case and spacing), or that starts with its `ID`. Options that themselves contain a comma can be miscounted in a Google Forms `multi` export; avoid commas in options of `multi` items.

## Converting `analysis.csv` to a spreadsheet

`analysis.csv` opens in Excel, Numbers, LibreOffice and Google Sheets as is. If a team wants `.xlsx`, convert it in the spreadsheet tool (or, where pandas and openpyxl are available, `python3 -c "import pandas as pd; pd.read_csv('analysis.csv').to_excel('analysis.xlsx', index=False)"`). The CSV stays the file of record because it diffs.
