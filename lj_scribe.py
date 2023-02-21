import collections

import flask

from ljm_constants import ljmmm

UnresolvedToResolvedPair = collections.namedtuple(
    "UnresolvedToResolvedPair",
    ["unresolved", "resolved"]
)


UnresolvedWithResolvedGrouping = collections.namedtuple(
    "UnresolvedWithResolvedGrouping",
    ["resolved", "unresolved"]
)

REGISTERS_TEMPLATE_STR = "@registers%s:%s"
TITLE_TEMPLATE_STR = "(%s)"
DEVICE_TYPES_TEMPLATE_STR = "[%s]"
SUBTAG_TEMPLATE_STR = "%s#(%d:%d:%d)%s"
SUBTAG_TEMPLATE_STR_DEFAULT_GAP = "%s#(%d:%d)%s"

MISSING_REG_MSG_TEMPLATE = "%s register not found"


class RegisterNotFoundError(Exception):
    def __init__(self, missing_reg_name):

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, MISSING_REG_MSG_TEMPLATE % missing_reg_name)

        self.missing_reg_name = missing_reg_name


def parsed_sub_tag_to_names(entry):
    if not entry.includes_ljmmm:
        return [entry.prefix]

    if entry.num_between_regs: num_between_regs = entry.num_between_regs
    else: num_between_regs = 1

    enumeration_src = (
        entry.prefix,
        entry.start_num,
        entry.start_num + num_between_regs * (entry.num_regs-1),
        entry.num_between_regs,
        entry.postfix
    )
    return ljmmm.generate_int_enumeration(enumeration_src)


def parsed_tag_to_names(tag_entries):
    return list(map(parsed_sub_tag_to_names, tag_entries))


def get_unres_reg_names_by_subtag_name(tag_names, unres_regs_by_res_name):
    return [(x, unres_regs_by_res_name[x]) for x in tag_names]


def get_unres_reg_names_for_tag_names(tag, unres_regs_by_res_name):
    return [get_unres_reg_names_by_subtag_name(x, unres_regs_by_res_name) for x in tag]


def resolve_registers_by_name_in_tuple(target_tuple, res_regs_by_res_name):
    return [(res_regs_by_res_name[x[0]], x[1]) for x in target_tuple]


def resolve_registers_by_name_in_tag(target_tag, res_regs_by_res_name):
    return [resolve_registers_by_name_in_tuple(x, res_regs_by_res_name) for x in target_tag]


def convert_unresolved_to_resolved_tuple(target_tuple):
    return [UnresolvedToResolvedPair(x[1], x[0]) for x in target_tuple]


def convert_unresolved_to_resolved_tag(target_tag):
    return list(map(
        convert_unresolved_to_resolved_tuple,
        target_tag
    ))


def find_classes(tag_entries, dev_regs):
    regs_tuple_res_name_first = [(x[1]["name"], x[0]) for x in dev_regs]
    unres_regs_by_res_name = dict(regs_tuple_res_name_first)
    res_regs_by_res_name = dict(
        [(x[1]["name"], x[1]) for x in dev_regs]
    )

    tag_names = list(map(parsed_tag_to_names, tag_entries))

    try:
        res_name_to_unres_entry_tuple = [get_unres_reg_names_for_tag_names(
                x,
                unres_regs_by_res_name
            ) for x in tag_names]
    except KeyError as e:
        raise RegisterNotFoundError(e)

    res_entry_to_unres_entry_tuple = [resolve_registers_by_name_in_tag(x, res_regs_by_res_name) for x in res_name_to_unres_entry_tuple]

    return list(map(
        convert_unresolved_to_resolved_tag,
        res_entry_to_unres_entry_tuple
    ))


def fix_not_found_reg_names(target_code, not_found_reg_names):
    """Fix the target code by moving unrecognized register names to the end.

    @param target_code: Something like "@registers:STREAM_DATA_CR,MOOCOW,AIN0"
    @type target_code: str
    @param not_found_reg_names: List of names to strip from the target code
    @type not_found_reg_names: Iterable of str
    @return the fixed target code. Something like:
        "@registers:STREAM_DATA_CR,AIN0 Unknown register(s): [MOOCOW]"
    @return type: str
    """
    if not len(not_found_reg_names):
        return target_code

    colon_index = target_code.index(':') + 1
    prefix = target_code[:colon_index]
    regs = target_code[colon_index:].split(',')
    return prefix + ','.join([
        reg for reg in regs if reg not in not_found_reg_names
    ]) + ' Unknown register(s): ' + ', '.join(not_found_reg_names)


def find_classes_from_map(tag_entries, reg_maps, not_found_reg_names):
    """Find the classes for a given set of names, given a list of device maps.

    @param tag_entries: the names get get classes for
    @param reg_maps: the list of device maps
    @type reg_maps: dict
    """
    # Flatten reg_maps
    all_regs = []
    for dev_regs in list(reg_maps.values()):
        all_regs.extend(dev_regs)

    regs_tuple_res_name_first = [(x[1]["name"], x[0]) for x in all_regs]
    unres_regs_by_res_name = dict(regs_tuple_res_name_first)

    regs_tuple_res_altnames_first = [(x[1]["altnames"], x[0]) for x in all_regs]

    def inner_expand_by_altname(unexpanded_altname_list):
        for each_unexpanded_tuple in unexpanded_altname_list:
            for altname in each_unexpanded_tuple[0]:
                yield (altname, each_unexpanded_tuple[1])

    regs_tuple_res_altname_first = \
        [x for x in inner_expand_by_altname(regs_tuple_res_altnames_first)]
    unres_regs_by_res_altname = dict(regs_tuple_res_altname_first)

    def inner_create_tuple(tag_entries, unres_regs_by_res_name):
        tag_names = list(map(parsed_tag_to_names, tag_entries))
        return [get_unres_reg_names_for_tag_names(
                x,
                unres_regs_by_res_name
            ) for x in tag_names]

    unres_regs_by_res_name.update(unres_regs_by_res_altname)

    def inner_try_remove_wrapper(tag_entries, unres_regs_by_res_name):
        while True:
            try:
                return inner_create_tuple(
                    tag_entries,
                    unres_regs_by_res_name
                )
            except KeyError as e:
                # Remove the register which could not be found in reg_maps
                # TODO: Add the offending register to a list, which we'll return
                found = False
                for entry in tag_entries[0]:
                    if entry.prefix == e:
                        found = True
                        tag_entries[0].remove(entry)
                        not_found_reg_names.append(e)
                if not found:
                    raise RegisterNotFoundError(e)

    res_name_to_unres_entry_tuple = inner_try_remove_wrapper(
        tag_entries,
        unres_regs_by_res_name
    )

    res_regs_by_res_name = dict(
        [(x[1]["name"], x[1]) for x in all_regs]
    )
    res_regs_by_res_name.update(dict(
        [x for x in inner_expand_by_altname([(x[1]["altnames"], x[1]) for x in all_regs])]
    ))

    res_entry_to_unres_entry_tuple = [resolve_registers_by_name_in_tag(x, res_regs_by_res_name) for x in res_name_to_unres_entry_tuple]

    return list(map(
        convert_unresolved_to_resolved_tag,
        res_entry_to_unres_entry_tuple
    ))


def fia_find_subtags_by_class(unresolved_resolved_pairs):
    ret_dict = collections.OrderedDict()

    for entry in unresolved_resolved_pairs:
        unresolved = entry[0].unresolved
        name = unresolved["name"]
        grouping = UnresolvedWithResolvedGrouping(
            [x.resolved for x in entry], unresolved
        )
        ret_dict[name] = grouping

    return ret_dict


def find_subtags_by_class(unresolved_resolved_pairs, dev_regs):
    ret_dict = collections.OrderedDict()

    # unres_regs_by_unres_name = dict(
    #     map(lambda x: (x[0]["name"], x[0]), dev_regs)
    # )

    for entry in unresolved_resolved_pairs:
        unresolved = entry[0].unresolved
        name = unresolved["name"]
        grouping = UnresolvedWithResolvedGrouping(
            [x.resolved for x in entry], unresolved)
        ret_dict[name] = grouping

    return ret_dict


def fia_organize_tag_by_class(target_tag):
    return [fia_find_subtags_by_class(x) for x in target_tag]

def organize_tag_by_class(target_tag, dev_regs):
    return [find_subtags_by_class(x, dev_regs) for x in target_tag]


def render_tag_summary(subtag_by_class, orig_tags, orig_tag_str, expand=False):
    return flask.render_template(
        "tag_summary_template.html",
        tags=list(zip(orig_tags, list(subtag_by_class.values()))),
        orig_str=orig_tag_str,
        expand = expand
    )


def find_original_tag_str(parsed_tag):
    tag_strs = []

    for sub_tag in parsed_tag:
        if not sub_tag.includes_ljmmm:
            tag_strs.append(sub_tag.prefix)
        elif sub_tag.num_between_regs:
            template_values = (
                sub_tag.prefix,
                sub_tag.start_num,
                sub_tag.num_regs,
                sub_tag.num_between_regs,
                sub_tag.postfix
            )
            tag_strs.append(SUBTAG_TEMPLATE_STR % template_values)
        else:
            template_values = (
                sub_tag.prefix,
                sub_tag.start_num,
                sub_tag.num_regs,
                sub_tag.postfix
            )
            tag_strs.append(SUBTAG_TEMPLATE_STR_DEFAULT_GAP % template_values)

    prefix_section = ''
    if parsed_tag[0].title != "":
        prefix_section += TITLE_TEMPLATE_STR % parsed_tag[0].title
    if len(parsed_tag[0].device_types):
        prefix_section += DEVICE_TYPES_TEMPLATE_STR % (
            ",".join(parsed_tag[0].device_types)
        )

    return REGISTERS_TEMPLATE_STR % (prefix_section, ",".join(tag_strs))
