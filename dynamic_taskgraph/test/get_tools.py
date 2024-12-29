import importlib
import pkgutil
import crewai_tools


def get_tools() -> list:
    tool_list = []
    for _, module_name, _ in pkgutil.iter_modules(crewai_tools.__path__):
        module = importlib.import_module(f"crewai_tools.{module_name}")
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type):
                tool_list.append(attribute)
    return tool_list

if __name__ == "__main__":
    print("Available tools:", get_tools())