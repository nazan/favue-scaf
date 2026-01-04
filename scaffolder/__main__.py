#!/usr/bin/env python3
"""
FastAPI + Vue.js Project Scaffolding Tool
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from string import Template


class Scaffolder:
    def __init__(self):
        self.project_name = None
        self.project_path = None
        self.backend_name = None
        self.frontend_name = None
        self.db_name = None
        self.api_port = 8000
        self.web_port = 5173
        self.db_port = 3306
        self.db_test_port = 3307  # Test database port (main port + 1)
        self.uid = os.getuid()
        self.gid = os.getgid()
        
        # Get templates directory
        # When running in Docker, templates are in /app/templates
        # When running as script, templates are relative to the package
        if Path('/app/templates').exists():
            # Running in Docker
            self.base_dir = Path('/app')
        else:
            # Running as script (development)
            self.base_dir = Path(__file__).parent.parent
        self.templates_dir = self.base_dir / 'templates'
    
    def collect_input(self):
        """Interactive input collection"""
        print("=" * 60)
        print("FastAPI + Vue.js Project Scaffolder")
        print("=" * 60)
        print()
        
        # Project name
        while True:
            self.project_name = input("Project name (e.g., myapp): ").strip()
            if self.project_name and self.project_name.replace('-', '').replace('_', '').isalnum():
                break
            print("Invalid project name. Use alphanumeric, dashes, or underscores.")
        
        # Project location
        # When running in Docker, default to /workspace
        workspace = Path('/workspace')
        if workspace.exists():
            default_path = workspace / self.project_name
            default_display = f"/workspace/{self.project_name}"
        else:
            default_path = Path.home() / "projects" / self.project_name
            default_display = str(default_path)
        
        path_input = input(f"Project location [{default_display}]: ").strip()
        if path_input:
            self.project_path = Path(path_input)
        else:
            self.project_path = default_path
        
        # Database name
        self.db_name = input(f"Database name [{self.project_name}]: ").strip() or self.project_name
        
        # Ports
        port_input = input(f"API port [{self.api_port}]: ").strip()
        if port_input:
            try:
                self.api_port = int(port_input)
            except ValueError:
                pass
        
        port_input = input(f"Web port [{self.web_port}]: ").strip()
        if port_input:
            try:
                self.web_port = int(port_input)
            except ValueError:
                pass
        
        port_input = input(f"Database port [{self.db_port}]: ").strip()
        if port_input:
            try:
                self.db_port = int(port_input)
                # Auto-set test port to main port + 1
                self.db_test_port = self.db_port + 1
            except ValueError:
                pass
        
        # Derived names
        self.backend_name = f"{self.project_name}-core"
        self.frontend_name = f"{self.project_name}-web"
        
        print()
        print("Configuration:")
        print(f"  Project: {self.project_name}")
        print(f"  Location: {self.project_path}")
        print(f"  Backend: {self.backend_name}")
        print(f"  Frontend: {self.frontend_name}")
        print(f"  Database: {self.db_name}")
        print(f"  Ports: API={self.api_port}, Web={self.web_port}, DB={self.db_port}, DB_TEST={self.db_test_port}")
        print()
        
        confirm = input("Proceed? [Y/n]: ").strip().lower()
        if confirm and confirm != 'y':
            print("Aborted.")
            sys.exit(0)
    
    def check_prerequisites(self):
        """Check for required tools"""
        print("Checking prerequisites...")
        # Only check for git - docker/docker-compose are needed on host, not in container
        required = {
            'git': ['git', '--version'],
        }
        
        missing = []
        for tool, cmd in required.items():
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                print(f"  ✓ {tool}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"  ✗ {tool} not found")
                missing.append(tool)
        
        if missing:
            print(f"\nError: Missing required tools: {', '.join(missing)}")
            sys.exit(1)
        
        print("  All prerequisites met!\n")
    
    def create_directory_structure(self):
        """Create main project directory"""
        # When running in Docker, ensure path is within /workspace
        workspace = Path('/workspace')
        if workspace.exists():
            # If path is absolute but outside workspace, make it relative to workspace
            if self.project_path.is_absolute() and not str(self.project_path).startswith(str(workspace)):
                self.project_path = workspace / self.project_name
            # If path is relative, make it relative to workspace
            elif not self.project_path.is_absolute():
                self.project_path = workspace / self.project_path
        
        print(f"Creating project directory: {self.project_path}")
        if self.project_path.exists():
            response = input(f"Directory {self.project_path} exists. Overwrite? [y/N]: ").strip().lower()
            if response != 'y':
                print("Aborted.")
                sys.exit(0)
            shutil.rmtree(self.project_path)
        
        self.project_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.project_path)
    
    def init_git_repo(self):
        """Initialize main git repository"""
        print("Initializing git repository...")
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        # Configure git (required for commits)
        subprocess.run(['git', 'config', 'user.name', 'Scaffolder'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'scaffolder@local'], check=True, capture_output=True)
        print("  ✓ Git repository initialized\n")
    
    def create_backend_submodule(self):
        """Create backend submodule"""
        print(f"Creating backend submodule: {self.backend_name}")
        backend_path = Path(self.backend_name)
        backend_path.mkdir()
        
        # Initialize git repo in backend
        os.chdir(backend_path)
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        
        # Configure git (required for commits)
        subprocess.run(['git', 'config', 'user.name', 'Scaffolder'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'scaffolder@local'], check=True, capture_output=True)
        
        # Create backend structure
        self._create_backend_files()
        
        # Initial commit
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True, capture_output=True)
        
        os.chdir('..')
        
        # Add as submodule (using relative path)
        subprocess.run([
            'git', 'submodule', 'add', 
            f'./{self.backend_name}', 
            self.backend_name
        ], check=True, capture_output=True)
        
        print(f"  ✓ Backend submodule created\n")
    
    def create_frontend_submodule(self):
        """Create frontend submodule"""
        print(f"Creating frontend submodule: {self.frontend_name}")
        frontend_path = Path(self.frontend_name)
        frontend_path.mkdir()
        
        # Initialize git repo in frontend
        os.chdir(frontend_path)
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        
        # Configure git (required for commits)
        subprocess.run(['git', 'config', 'user.name', 'Scaffolder'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'scaffolder@local'], check=True, capture_output=True)
        
        # Create frontend structure
        self._create_frontend_files()
        
        # Initial commit
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True, capture_output=True)
        
        os.chdir('..')
        
        # Add as submodule
        subprocess.run([
            'git', 'submodule', 'add',
            f'./{self.frontend_name}',
            self.frontend_name
        ], check=True, capture_output=True)
        
        print(f"  ✓ Frontend submodule created\n")
    
    def create_main_files(self):
        """Create main project files"""
        print("Creating main project files...")
        self._create_compose_yml()
        self._create_makefile()
        self._create_env_example()
        self._create_gitignore()
        self._create_readme()
        print("  ✓ Main files created\n")
    
    def finalize(self):
        """Finalize setup"""
        print("Finalizing...")
        # Initial commit for main repo
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial project setup'], check=True, capture_output=True)
        
        print()
        print("=" * 60)
        print("Project scaffolded successfully!")
        print("=" * 60)
        print()
        print(f"Next steps:")
        print(f"  1. cd {self.project_path}")
        print(f"  2. make setup")
        print()
    
    def _create_backend_files(self):
        """Create all backend files"""
        # Directory structure
        dirs = [
            'app/api/v1',
            'app/core',
            'app/db',
            'app/services',
            'app/schemas',
            'alembic/versions',
            'tests',
            'logs',
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        for init_file in [
            'app/__init__.py',
            'app/api/__init__.py',
            'app/api/v1/__init__.py',
            'app/core/__init__.py',
            'app/db/__init__.py',
            'app/services/__init__.py',
            'app/schemas/__init__.py',
            'tests/__init__.py',
        ]:
            Path(init_file).touch()
        
        # Copy and process template files
        backend_templates = [
            ('Dockerfile', 'Dockerfile'),
            ('requirements.txt', 'requirements.txt'),
            ('pytest.ini', 'pytest.ini'),
            ('alembic.ini', 'alembic.ini'),
            ('.env.example', '.env.example'),
            ('test.env.example', 'test.env.example'),
            ('.gitignore', '.gitignore'),
            ('.dockerignore', '.dockerignore'),
            ('app/main.py', 'app/main.py'),
            ('app/config.py', 'app/config.py'),
            ('app/log_setup.py', 'app/log_setup.py'),
            ('app/exceptions.py', 'app/exceptions.py'),
            ('app/service_init.py', 'app/service_init.py'),
            ('app/core/di.py', 'app/core/di.py'),
            ('app/db/session.py', 'app/db/session.py'),
            ('app/db/tables.py', 'app/db/tables.py'),
            ('app/services/utility_service.py', 'app/services/utility_service.py'),
            ('app/schemas/utility_schema.py', 'app/schemas/utility_schema.py'),
            ('app/api/v1/main_routes.py', 'app/api/v1/main_routes.py'),
            ('alembic/env.py', 'alembic/env.py'),
            ('alembic/script.py.mako', 'alembic/script.py.mako'),
            ('tests/conftest.py', 'tests/conftest.py'),
            ('tests/test_utility_service.py', 'tests/test_utility_service.py'),
        ]
        
        for template_rel, output_rel in backend_templates:
            self._process_template(f'backend/{template_rel}', output_rel)
    
    def _create_frontend_files(self):
        """Create all frontend files"""
        # Directory structure
        dirs = [
            'src/router',
            'src/services',
            'src/views',
            'src/components',
            'src/composables',
            'src/utils',
            'public',
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        
        # Copy and process template files
        frontend_templates = [
            ('Dockerfile', 'Dockerfile'),
            ('package.json', 'package.json'),
            ('vite.config.js', 'vite.config.js'),
            ('entrypoint.sh', 'entrypoint.sh'),
            ('.gitignore', '.gitignore'),
            ('index.html', 'index.html'),
            ('src/main.js', 'src/main.js'),
            ('src/App.vue', 'src/App.vue'),
            ('src/config.js', 'src/config.js'),
            ('src/router/index.js', 'src/router/index.js'),
            ('src/services/api.js', 'src/services/api.js'),
            ('src/views/HomeView.vue', 'src/views/HomeView.vue'),
        ]
        
        for template_rel, output_rel in frontend_templates:
            self._process_template(f'frontend/{template_rel}', output_rel)
        
        # Make entrypoint executable
        os.chmod('entrypoint.sh', 0o755)
    
    def _create_compose_yml(self):
        """Create docker-compose.yml"""
        self._process_template('main/compose.yml', 'compose.yml')
    
    def _create_makefile(self):
        """Create Makefile"""
        self._process_template('main/Makefile', 'Makefile')
    
    def _create_env_example(self):
        """Create .env.example"""
        env_content = f"""PROJECT_NAME={self.project_name}
BACKEND_NAME={self.backend_name}
FRONTEND_NAME={self.frontend_name}
DB_NAME={self.db_name}
API_PORT={self.api_port}
WEB_PORT={self.web_port}
DB_PORT={self.db_port}
DB_TEST_PORT={self.db_test_port}
UID={self.uid}
GID={self.gid}
"""
        Path('.env.example').write_text(env_content)
    
    def _create_gitignore(self):
        """Create .gitignore"""
        self._process_template('main/.gitignore', '.gitignore')
    
    def _create_readme(self):
        """Create README.md"""
        self._process_template('main/README.md', 'README.md')
    
    def _process_template(self, template_path, output_path):
        """Process a template file with variable substitution"""
        template_file = self.templates_dir / template_path
        
        if not template_file.exists():
            print(f"Warning: Template not found: {template_file}")
            return
        
        # Read template
        template_content = template_file.read_text()
        
        # Substitute variables
        template = Template(template_content)
        content = template.safe_substitute(
            PROJECT_NAME=self.project_name,
            BACKEND_NAME=self.backend_name,
            FRONTEND_NAME=self.frontend_name,
            DB_NAME=self.db_name,
            API_PORT=self.api_port,
            WEB_PORT=self.web_port,
            DB_PORT=self.db_port,
            DB_TEST_PORT=self.db_test_port,
            UID=self.uid,
            GID=self.gid,
        )
        
        # Write file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)


def main():
    try:
        scaffolder = Scaffolder()
        scaffolder.collect_input()
        scaffolder.check_prerequisites()
        scaffolder.create_directory_structure()
        scaffolder.init_git_repo()
        scaffolder.create_backend_submodule()
        scaffolder.create_frontend_submodule()
        scaffolder.create_main_files()
        scaffolder.finalize()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

