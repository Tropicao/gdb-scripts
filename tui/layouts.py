# Heavily inspired, if not completely copied, from
# https://undo.io/resources/enhance-gdb-with-tui/

import gdb

class ScrollableWindow: 
    """ 
    Base class for displaying a GDB command in a scrollable TUI window. 
    Subclasses must define the class attributes `name`, `title` and `gdb_command`. 
    """
    name = None
    title = None 
    gdb_command = None

    def __init_subclass__(cls):
        if cls.name is None or cls.title is None or cls.gdb_command is None:
            raise TypeError("Subclass must define `name`, `title` and `gdb_command` attributes")
        gdb.register_window_type(cls.name, cls)
        gdb.execute(f"tui new-layout {cls.name} {cls.name} 1 status 1 cmd 1") 

    def __init__(self, tui_window):
        self._tui_window = tui_window
        self._tui_window.title = self.title
        
        # When scrolling we use cached lines to avoid regenerating the content.
        self.use_cached_lines = False
        self.cached_lines = None
        self.vscroll_offset = 0
        self.hscroll_offset = 0
        gdb.events.before_prompt.connect(self.render)

    def close(self):
        gdb.events.before_prompt.disconnect(self.render)
    
    def get_lines(self):
        """
        Return the content of the window as lines.
        """
        return gdb.execute(self.gdb_command, to_string=True).splitlines()

    def get_lines_or_error(self): 
        """ 
        Return the content to be displayed in this window as a list of lines, or exception 
        message if a gdb.error occurs. 
        """ 
        try: 
            return self.get_lines() 
        except gdb.error as exc: 
            return str(exc).splitlines() 
    def get_viewport_content(self): 
        """ 
        Return the content that should be displayed in the window, 
        taking into account the current window size and scroll offsets. 
        """ 
        if self.use_cached_lines and self.cached_lines is not None: 
            lines, content_height, content_width = self.cached_lines 
            self.use_cached_lines = False 
        else: 
            lines = self.get_lines_or_error() 
            if lines: 
                content_height = len(lines) 
                content_width = max(map(len, lines)) 
                self.cached_lines = (lines, content_height, content_width) 

        if not lines: 
            return "" 

        # Limit scroll to the content height 
        window_height = self._tui_window.height 
        self.vscroll_offset = min(content_height - window_height, self.vscroll_offset) 
        self.vscroll_offset = max(0, self.vscroll_offset)

        # Truncate content vertically 
        free_height = window_height - content_height 
        if free_height < 0: 
            # We have to truncate the height, after adjusting for scroll. 
            scrolled_free_height = window_height - (content_height - self.vscroll_offset) 
            if scrolled_free_height >= 0: 
                lines = lines[self.vscroll_offset :] 
            else: 
                lines = lines[self.vscroll_offset : self.vscroll_offset + window_height]

        # Limit scroll to the content width 
        window_width = self._tui_window.width - 1
        self.hscroll_offset = min(content_width - window_width, self.hscroll_offset) 
        self.hscroll_offset = max(0, self.hscroll_offset) 

        # Truncate content horizontally 
        truncated_lines = [l[self.hscroll_offset:self.hscroll_offset + window_width] for l in lines]

        return "\n".join(truncated_lines) 

    def render(self): 
        if not self._tui_window.is_valid(): 
            return 
        output = self.get_viewport_content() 
        self._tui_window.write(output, True) 

    def vscroll(self, num): 
        self.vscroll_offset += num 
        self.use_cached_lines = True 
        self.render() 

    def hscroll(self, num): 
        self.hscroll_offset += num 
        self.use_cached_lines = True 
        self.render()

class BacktraceWindow(ScrollableWindow): 
    name = "backtrace" 
    title = "Backtrace" 
    gdb_command = "backtrace"

class LocalsWindow(ScrollableWindow): 
    name = "locals" 
    title = "Local Variables" 
    gdb_command = "info locals"
