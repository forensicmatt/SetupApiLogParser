import re
import logging
import collections

INDENT_SIZE = 5
RE_BOOT_SESSION = re.compile(b"^\[Boot Session: (.*)\]$")
RE_SECTION_TITLE = re.compile(b"^>>>[ ]{1,}\[(.*)\]$")
RE_SECTION_START = re.compile(b"^>>>[ ]{1,}Section start (.*)$")
RE_SECTION_END = re.compile(b"^<<<[ ]{1,}Section end (.*)$")
RE_SECTION_STATUS = re.compile(b"^<<<[ ]{1,}\[Exit status: (.*)\]$")
RE_GROUP_START = re.compile(b"^\{(.*)\} (\d\d:\d\d:\d\d\.\d\d\d)$")
RE_GROUP_END = re.compile(b"^\{(.*) - exit\((.*)\)\} (\d\d:\d\d:\d\d.\d\d\d)$")
RE_SPACE = re.compile(b"^\s*")

class SetupApiLogHandler(object):
    def __init__(self, file_io, source_description):
        self.source_description = source_description
        self._file_io = file_io
        self._file_io.seek(0)
        self._content_lines = self._file_io.read().split(b"\r\n")
        self.header = None
        self.current_boot_session = None
        self._read_header()

    def _read_header(self):
        header_line = self._content_lines[0]
        if not header_line.startswith(b"[Device Install Log]"):
            raise(Exception("Log does not start with [Device Install Log]"))

        self.header = collections.OrderedDict([])
        for line in self._content_lines[1:]:
            if line.startswith(b"[BeginLog]"):
                break

            line = line.strip()
            if line:
                parts = line.split(b" = ")

                if len(parts) == 2:
                    self.header[parts[0]] = parts[1]
                else:
                    logging.warning(
                        "Header attribute line has more than 2 parts: {}".format(parts)
                    )

    def iter_sections(self):
        section_flag = False
        section_lines = []
        for line in self._content_lines:
            boot_session = RE_BOOT_SESSION.match(line)
            if boot_session:
                self.current_boot_session = boot_session.group(1).replace(b"/", b"-").decode("utf-8")
                logging.debug("Boot Session: {}".format(
                    self.current_boot_session
                ))

            section_title = RE_SECTION_TITLE.match(line)
            if section_title:
                section_flag = True

            section_final = RE_SECTION_STATUS.match(line)

            if section_flag:
                section_lines.append(line)

            if section_final:
                sh = SectionHandler(
                    section_lines,
                    boot_session=self.current_boot_session
                )
                yield sh
                section_flag = False
                section_lines = []


class SectionHandler(object):
    def __init__(self, lines, boot_session=None):
        self.title = collections.OrderedDict([])
        self.section_start = None
        self.body = []
        self.section_end = None
        self.exit_status = None
        self.boot_session = boot_session

        body_lines = []
        for line in lines:
            section_title = RE_SECTION_TITLE.match(line)
            if section_title:
                parts = section_title.group(1).split(b" - ")
                if len(parts) == 1:
                    self.title['section_title'] = parts[0].decode("utf-8")
                elif len(parts) == 2:
                    self.title['section_title'] = parts[0].decode("utf-8")
                    self.title['instance_identifier'] = parts[1].decode("utf-8")
                else:
                    logging.warning("Section title with {} parts is not handled.".format(
                        len(parts)
                    ))
                continue

            section_start = RE_SECTION_START.match(line)
            if section_start:
                self.section_start = section_start.group(1).replace(b"/", b"-").decode("utf-8")
                continue

            section_end = RE_SECTION_END.match(line)
            if section_end:
                self.section_end = section_end.group(1).replace(b"/", b"-").decode("utf-8")
                continue

            section_status = RE_SECTION_STATUS.match(line)
            if section_status:
                self.exit_status = section_status.group(1).decode("utf-8")
                continue

            body_lines.append(line)

        self._parse_body(body_lines)

    def _parse_body(self, body_lines):
        for line in body_lines:
            lh = LineHandler(line)

            self.body.append(lh.as_dict())

    def as_dict(self):
        record = collections.OrderedDict([])
        if self.boot_session:
            record['boot_session'] = self.boot_session

        record.update(self.title)
        record['section_start'] = self.section_start
        record['body'] = self.body
        record['section_end'] = self.section_end
        record['exit_status'] = self.exit_status
        return record


class LineHandler(object):
    INDENT_SIZE = 5

    def __init__(self, line):
        self.message_level = None
        self.event_category = None
        self.indent_level = None
        self.content = None

        entry_type = line[0:5]
        m_count = entry_type.count(b"!")
        remainder = line[5:]

        if m_count == 0:
            self.message_level = 'info'
        elif m_count == 1:
            self.message_level = 'warning'
        elif m_count == 3:
            self.message_level = 'error'
        else:
            logging.warning("message level unhandled. ! count: {}".format(m_count))
            self.message_level = str(m_count)

        event_category, remainder = remainder.strip().split(b": ", 1)
        self.event_category = event_category.decode("utf-8")

        indent_pattern = b" " * INDENT_SIZE
        index = len(RE_SPACE.match(remainder).group(0))
        self.indent_level = remainder[0:index].count(indent_pattern)

        index = self.indent_level * INDENT_SIZE
        self.content = remainder[index:].decode("utf-8")

    def as_dict(self):
        record = collections.OrderedDict([])
        record['message_level'] = self.message_level
        record['event_category'] = self.event_category
        record['indent_level'] = self.indent_level
        record['content'] = self.content
        return record
