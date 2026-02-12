# HandeeFramer Test Examples

## Example 1: Simple Indented Structure
```
myproject
  src
    main.py
    utils.py
  tests
    test_main.py
  README.md
```

## Example 2: Shorthand Notation
```
myproject/src/main.py
myproject/src/utils.py
myproject/tests/test_main.py
myproject/README.md
```

## Example 3: Mixed Notation
```
frontend
  css/style.css
  css/reset.css
  js
    app.js
    utils.js
  index.html
backend/api/routes.py
backend/api/models.py
backend/config.py
```

## Example 4: Explicit Directories with Trailing Slash
```
project/
  src/
    main.cpp
    utils.cpp
  include/
    utils.h
  build/
  README.md
```

## Example 5: Multiple Root Items (Creates in Current Directory)
```
frontend
  index.html
backend
  server.py
database
  schema.sql
```

## Example 6: Deep Nesting
```
game_engine
  src
    core
      engine.cpp
      renderer.cpp
    physics
      collision.cpp
      rigidbody.cpp
    audio
      sound_manager.cpp
  assets
    textures
      player.png
      enemy.png
    sounds
      music.ogg
      sfx.ogg
  docs
    api_reference.md
```

## Example 7: Windows-Style Backslashes
```
project\src\main.cpp
project\src\utils.cpp
project\include\utils.h
```

## Example 8: Mixed Slashes (Both Work)
```
project/src\main.cpp
project\src/utils.cpp
project/include\utils.h
```

## Example 9: Web Application Structure
```
webapp
  public
    css
      main.css
      responsive.css
    js
      app.js
      vendor.js
    images
      logo.png
  server
    routes
      api.js
      auth.js
    models
      user.js
      post.js
    controllers
      userController.js
      postController.js
  config
    database.js
    environment.js
  package.json
  server.js
```

## Example 10: Python Package with Tests
```
mypackage/
  __init__.py
  core/
    __init__.py
    engine.py
    processor.py
  utils/
    __init__.py
    helpers.py
    validators.py
  tests/
    __init__.py
    test_core.py
    test_utils.py
  docs/
    getting_started.md
    api_reference.md
  setup.py
  requirements.txt
  README.md
  LICENSE
```

## Example 11: Box-Drawing Format (from documentation)
```
📁 promptin-app/
│
├── 📄 package.json
├── 📄 tsconfig.json
├── 📄 next.config.js
│
├── 📁 types/
│   └── index.ts
│
├── 📁 server/
│   ├── database/
│   │   ├── mongodb.ts
│   │   └── redis.ts
│   │
│   └── workers/
│       └── base/
│           ├── ModelWorker.ts
│           └── WorkerPool.ts
│
└── 📁 app/
    ├── layout.tsx
    └── page.tsx
```

## Example 12: Box-Drawing with Emojis
```
🚀 my-awesome-project/
│
├── 📦 packages/
│   ├── 🎨 ui/
│   │   ├── Button.tsx
│   │   └── Input.tsx
│   │
│   └── 🔧 utils/
│       └── helpers.ts
│
├── 📚 docs/
│   └── README.md
│
└── ⚙️ config/
    └── settings.json
```

## Example 13: Complex Nested Box-Drawing
```
project/
│   ├── 📄 package.json
│   │
│   ├── 📁 server/
│   │   ├── database/
│   │   │   ├── mongodb.ts
│   │   │   └── models/
│   │   │       ├── User.ts
│   │   │       └── Post.ts
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.ts
│   │   │   │   └── posts.ts
│   │   │   │
│   │   │   └── middleware/
│   │   │       └── validation.ts
│   │   │
│   │   └── index.ts
│   │
│   └── 📁 client/
│       ├── components/
│       │   └── Header.tsx
│       │
│       └── app.tsx
```

## Example 14: Mixed Formats in One Document
```
📁 hybrid-project/
│
├── 📁 backend/
│   ├── server.py
│   └── database/
│       ├── models.py
│       └── schemas.py
│
├── frontend/src/App.tsx
├── frontend/src/components/Button.tsx
│
└── docs
    ├── API.md
    └── SETUP.md
```

## Notes on Box-Drawing Format

- **All emojis are automatically removed** (📁, 📄, 🚀, 🎨, etc.)
- **Box-drawing characters are stripped** (│, ├, └, ─, ┌, ┐, etc.)
- **Hierarchy is preserved** based on visual indentation
- **Perfect for documentation** - paste directly from README files
- **OS-compatible** - invalid filename characters are filtered out
- **Works seamlessly** with other notation styles
