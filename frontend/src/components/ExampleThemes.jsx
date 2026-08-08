const exampleThemes = [
  "🏴‍☠️ Pirates",
  "🚀 Space Adventure",
  "🐉 Dragon Kingdom",
  "🤖 Cyberpunk",
  "🧙 Fantasy",
]

function ExampleThemes({ onSelectTheme }) {
  return (
    <div className="examples">
      <h3>Try an example:</h3>
      <div className="example-list">
        {exampleThemes.map((theme) => (
          <button
            key={theme}
            type="button"
            className="theme-button"
            onClick={() => onSelectTheme(theme)}
          >
            {theme}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ExampleThemes;
