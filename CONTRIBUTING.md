<p align="center">
Translations <br>
<a href="CONTRIBUTING.md">🇬🇧 EN</a>
<a href="translations/es/CONTRIBUTING.md">🇪🇸 ES</a>
<a href="translations/pt-br/CONTRIBUTING.md">🇧🇷 PT-BR</a>
<a href="translations/zh-cn/CONTRIBUTING.md">🇨🇳 ZH-CN</a>
 <br><br>
</p>

# Contributing to Crivo

Hello there! 👋

So, you are interested in contributing to Crivo? 🤔 That's fantastic news!

Whether you are a seasoned developer or just starting out, your contributions are more than welcome. You might think, "Is my coding skill good enough?" The answer is: absolutely! Everyone has something valuable to add, and we are happy to work with you regardless of your experience level. If you are reading this, you are already ahead of many—newbies don't often learn how to contribute to GitHub projects! 😉

Here are some ways you can contribute to Crivo:

- Add new filtering capabilities or enhancements 🛠️
- Improve web scraping functionality 🌐
- Create or improve documentation (we would be immensely grateful for this!) 📖
- Fix bugs reported via GitHub issues 🐛
- Refactor the codebase to make it cleaner or more efficient ✨

Does this sound daunting? Don't worry! This document will guide you step by step through the process. Your contributions will not only improve Crivo but also earn you a spot in the contributors list—and our eternal gratitude! 🙏

We've set up a GitHub Discussions page for you to chat with the maintainers, ask questions, or suggest features. Alternatively, you can raise an issue directly on the GitHub repository.

---

## How to Contribute

There are plenty of ways to make Crivo even better! Below are a few specific areas where we would appreciate your help.

### 1. Add New Features 🛠️

Crivo thrives on its versatility. If you've an idea for a new feature—such as an additional scope filter, more robust parsing logic, or a new output format—feel free to implement it!

To get started:
- Fork the repository.
- Create a feature branch:
  ```bash
  git checkout -b feature/your-feature-name
  ```
- Implement your feature.
- Add tests for your feature (see below).
- Submit a pull request for review.

### 2. Improve Web Scraping 🌐

Crivo's web scraping capabilities are a key part of the project. If you've experience with web scraping or notice an area for improvement, your contributions would be invaluable. For instance:

- Enhance the way relative links are resolved.
- Add handling for edge cases like malformed HTML or unusual URL structures.

### 3. Create or Improve Documentation 📖

Documentation is the cornerstone of every successful project. Great documentation ensures that others can use and contribute to Crivo effectively.

Ways you can help:

- Add docstrings to the codebase.
- Improve existing documentation (e.g., README.md, this file).
- Translate the documentation into other languages.
- Write tutorials or usage guides.

Good documentation is just as valuable as code contributions, and we will greatly appreciate your help here!

### 4. Fix Bugs 🐛

We keep track of known issues in the GitHub Issues section. If you are up for a challenge:

- Choose a bug that interests you.
- Comment on the issue to let us know you are working on it.
- Submit your fix as a pull request.

Fixing bugs is a great way to familiarise yourself with the codebase while making an immediate impact.

### 5. Refactor the Codebase ✨

Not all of Crivo's codebase is perfect, and there's always room for improvement. If you spot opportunities to:

- Remove duplicate code.
- Make the code more modular or easier to read.
- Ensure the code follows Python's PEP8 standards.

Then dive in! Your refactoring efforts will make Crivo more maintainable for everyone.

## Writing Tests

When adding a new feature or fixing a bug, we encourage you to write tests to ensure everything works as expected. Crivo uses `pytest` for testing.

### How to Write Tests

1. Navigate to the `tests/` directory in the repository.
2. Create a new test file (e.g., `test_new_feature.py`) or add your tests to an existing file.
3. Write your test functions following the naming convention `test_<feature_or_bug>()`.

### Running Tests

To run the tests, use the following command in your terminal:

```bash
pytest
```

This will execute all the tests in the tests/ directory and display the results.


## Submitting Your Contributions

1. Once you've made your changes, push them to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Open a pull request against the main repository.

we will review your contribution, provide feedback if necessary, and merge it once it's ready. 🎉

## Thank You! 🙏

Contributing to open-source projects is incredibly rewarding, and we are thrilled you've chosen to contribute to Crivo. Your effort, time, and expertise are deeply appreciated. We can't wait to see what you build!

Happy coding!
