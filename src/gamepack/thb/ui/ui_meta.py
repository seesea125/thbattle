# -*- coding: utf-8 -*-
from .. import actions
from .. import cards
from .. import characters

import game
import types
import resource as gres
from client.ui import resource as cres

from utils import DataHolder, BatchList

def gen_metafunc(_for):
    def metafunc(clsname, bases, _dict):
        meta_for = _for.__dict__.get(clsname)
        data = DataHolder.parse(_dict)
        meta_for.ui_meta = data

    return metafunc

# -----BEGIN ACTIONS UI META-----
__metaclass__ = gen_metafunc(actions)

class DropCardStage:
    # choose_card meta
    text_valid = u'OK，就这些了'
    text = u'请弃牌…'

    def effect_string(act):
        if act.dropn:
            return u'|G【%s】|r弃掉了%d张牌。' % (
                act.target.ui_meta.char_name, act.dropn
            )

class DamageEffect:
    def effect_string(act):
        s, t = act.source, act.target
        if s:
            return u'|G【%s】|r对|G【%s】|r造成了%d点伤害。' % (
                s.ui_meta.char_name, t.ui_meta.char_name, act.amount
            )
        else:
            return u'|G【%s】|r受到了%d点无来源的伤害。' % (
                t.ui_meta.char_name, act.amount
            )

class LaunchCard:
    def effect_string_before(act):
        s, tl = act.source, BatchList(act.target_list)
        c = act.card
        from ..cards import Skill
        if isinstance(c, Skill):
            return c.ui_meta.effect_string(act)
        elif c:
            return u'|G【%s】|r对|G【%s】|r使用了|G%s|r。' % (
                s.ui_meta.char_name,
                u'】|r、|G【'.join(tl.ui_meta.char_name),
                act.card.ui_meta.name
            )

# -----END ACTIONS UI META-----

# -----BEGIN CARDS UI META-----
__metaclass__ = gen_metafunc(cards)

class HiddenCard:
    # action_stage meta
    image = cres.card_hidden
    name = u'这个是隐藏卡片，你不应该看到它'

    def is_action_valid(g, cl, target_list):
        return (False, u'这是BUG，你没法发动这张牌…')

class AttackCard:
    # action_stage meta
    image = gres.card_attack
    name = u'弹幕'

    def is_action_valid(g, cl, target_list):
        if not target_list:
            return (False, u'请选择弹幕的目标')

        if g.me is target_list[0]:
            return (True, u'您真的要自残么？！')
        else:
            return (True, u'来一发！')

class GrazeCard:
    # action_stage meta
    name = u'擦弹'
    image = gres.card_graze
    def is_action_valid(g, cl, target_list):
        return (False, u'你不能主动使用擦弹')

class WineCard:
    # action_stage meta
    name = u'酒'
    image = gres.card_wine
    def is_action_valid(g, cl, target_list):
        if g.me.tags.get('wine', False):
            return (True, u'你已经醉了，还要再喝吗？')
        return (True, u'青岛啤酒，神主也爱喝！')

class Wine:
    def effect_string(act):
        return u'|G【%s】|r喝醉了…' % act.target.ui_meta.char_name

class ExinwanCard:
    # action_stage meta
    name =u'恶心丸'
    image = gres.card_exinwan
    def is_action_valid(g, cl, target_list):
        return (True, u'哼，哼，哼哼……')

class ExinwanHandler:
    # choose_card meta
    text = u'请选择两张牌（不选则受到一点无源伤害）'
    text_valid = u'节操给你，离我远点！'

class UseGraze:
    # choose_card meta
    image = gres.card_graze
    text_valid = u'我闪！'
    text = u'请使用擦弹…'

    def effect_string(act):
        if not act.succeeded: return None
        t = act.target
        return u'|G【%s】|r使用了|G擦弹|r。' % t.ui_meta.char_name

class UseAttack:
    # choose_card meta
    text_valid = u'打架？来吧！'
    text = u'请打出一张弹幕…'

    def effect_string(act):
        if not act.succeeded: return None
        t = act.target
        return u'|G【%s】|r打出了|G弹幕|r。' % t.ui_meta.char_name

class HealCard:
    # action_stage meta
    image = gres.card_heal
    name = u'麻薯'

    def is_action_valid(g, cl, target_list):
        target = target_list[0]
        if not g.me is target:
            return (False, u'BUG!!!!')

        if target.life >= target.maxlife:
            return (False, u'您已经吃饱了')
        else:
            return (True, u'来一口，精神焕发！')

class UseHeal:
    # choose_card meta
    text_valid = u'神说，你不能在这里MISS'
    text = u'请选择一张【麻薯】…'

    def effect_string(act):
        if act.succeeded:
            return u'|G【%s】|r回复了%d点体力。' % (
                act.target.ui_meta.char_name, act.amount
            )

class DemolitionCard:
    # action_stage meta
    image = gres.card_demolition
    name = u'城管执法'

    def is_action_valid(g, cl, target_list):
        if not target_list:
            return (False, u'请选择拆除目标')

        target= target_list[0]
        if g.me is target:
            return (True, u'还是拆别人的吧…')
        elif not len(target.cards) + len(target.showncards) + len(target.equips) + len(target.fatetell):
            return (False, u'这货已经没有牌了')
        else:
            return (True, u'嗯，你的牌太多了')

class Demolition:
    def effect_string(act):
        if not act.succeeded: return None
        return u'|G【%s】|r卸掉了|G【%s】|r的|G%s|r。' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
            act.card.ui_meta.name,
        )

class RejectCard:
    # action_stage meta
    name = u'好人卡'
    image = gres.card_reject

    def is_action_valid(g, cl, target_list):
        return (False, u'你不能主动出好人卡')

class RejectHandler:
    # choose_card meta
    text_valid = u'对不起，你是一个好人…'
    text = u'请选择一张好人卡'

class Reject:
    def effect_string_before(act):
        return u'|G【%s】|r为|G【%s】|r受到的|G%s|r使用了|G好人卡|r。' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
            act.target_act.associated_card.ui_meta.name,
        )

class SealingArrayCard:
    # action_stage meta
    name = u'封魔阵'
    image = gres.card_sealarray
    tag_anim = gres.tag_sealarray

    def is_action_valid(g, cl, target_list):
        if len(target_list) != 1:
            return (False, u'请选择封魔阵的目标')
        t = target_list[0]
        if g.me is t:
            return (False, u'你不能跟自己过不去啊！')

        return (True, u'画个圈圈诅咒你！')

class SealingArray:
    def effect_string(act):
        tgt = act.target
        if act.succeeded:
            return u'|G【%s】|r被困在了封魔阵中' % tgt.ui_meta.char_name
        else:
            return u'封魔阵没有布置完善，|G【%s】|r侥幸逃了出来' % tgt.ui_meta.char_name

class NazrinRodCard:
    # action_stage meta
    name = u'探宝棒'
    image = gres.card_nazrinrod

    def is_action_valid(g, cl, target_list):
        t = target_list[0]
        assert t is g.me
        return (True, u'看看能找到什么好东西~')

class SinsackCard:
    # action_stage meta
    name = u'罪袋'
    image = gres.card_sinsack
    tag_anim = gres.tag_sinsack

    def is_action_valid(g, cl, target_list):
        target = target_list[0]
        if not g.me == target:
            return (False, u'BUG!!!!')

        return (True, u'别来找我！')

class Sinsack:
    def effect_string(act):
        tgt = act.target
        if act.succeeded:
            return u'罪袋终于找到了机会，将|G【%s】|r推倒了…' % tgt.ui_meta.char_name

def equip_iav(g, cl, target_list):
    t = target_list[0]
    assert t is g.me
    return (True, u'配上好装备，不再掉节操！')

class OpticalCloakCard:
    # action_stage meta
    name = u'光学迷彩'
    image = gres.card_opticalcloak
    image_small = gres.card_opticalcloak_small

    is_action_valid = equip_iav

class OpticalCloakSkill:
    # Skill
    name = u'光学迷彩'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class OpticalCloakHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【光学迷彩】吗？'

class OpticalCloak:
    def effect_string_before(act):
        return u'|G【%s】|r祭起了|G光学迷彩|r…' % (
            act.target.ui_meta.char_name,
        )

    def effect_string(act):
        if act.succeeded:
            return u'效果拔群！'
        else:
            return u'但是被看穿了…'

class GreenUFOCard:
    # action_stage meta
    name = u'绿色UFO'
    image = gres.card_greenufo
    image_small = gres.card_greenufo_small

    is_action_valid = equip_iav

class GreenUFOSkill:
    # Skill
    name = u'绿色UFO'
    no_display = True

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class RedUFOCard:
    # action_stage meta
    name = u'红色UFO'
    image = gres.card_redufo
    image_small = gres.card_redufo_small

    is_action_valid = equip_iav

class RedUFOSkill:
    # Skill
    name = u'红色UFO'
    no_display = True

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class YukariDimensionCard:
    # action_stage meta
    image = gres.card_yukaridimension
    name = u'紫的隙间'

    def is_action_valid(g, cl, target_list):
        if not target_list:
            return (False, u'请选择目标')

        target= target_list[0]
        if g.me is target:
            return (False, u'你不能对自己使用隙间')
        elif not len(target.cards):
            return (False, u'这货已经没有牌了')
        else:
            return (True, u'请把胖次给我！')

class YukariDimension:
    def effect_string(act):
        src, tgt = act.source, act.target
        if act.succeeded:
            return u'|G【%s】|r透过隙间拿走了|G【%s】|r的1张牌' % (
                src.ui_meta.char_name,
                tgt.ui_meta.char_name
            )

class DuelCard:
    # action_stage meta
    image = gres.card_duel
    name = u'弹幕战'

    def is_action_valid(g, cl, target_list):
        if not target_list:
            return (False, u'请选择弹幕战的目标')

        target= target_list[0]
        if g.me is target:
            return (False, u'你不能对自己使用弹幕战')
        else:
            return (True, u'来，战个痛快！')

class MapCannonCard:
    image = gres.card_mapcannon
    name = u'地图炮'

    def is_action_valid(g, cl, target_list):
        return (True, u'一个都不能跑！')

class SinsackCarnivalCard:
    image = gres.card_sinsackcarnival
    name = u'罪袋狂欢'

    def is_action_valid(g, cl, target_list):
        return (True, u'罪袋们来送水啦！')

class HakuroukenCard:
    # action_stage meta
    name = u'白楼剑'
    image = gres.card_hakurouken
    image_small = gres.card_hakurouken_small

    is_action_valid = equip_iav

class HakuroukenSkill:
    # Skill
    name = u'白楼剑'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class Hakurouken:
    def effect_string_before(act):
        a = act.action
        src, tgt = a.source, a.target
        return u'|G【%s】|r祭起了|G白楼剑|r，直斩|G【%s】|r的魂魄！' % (
            t.ui_meta.char_name
        )

class ElementalReactorCard:
    # action_stage meta
    name = u'八卦炉'
    image = gres.card_reactor
    image_small = gres.card_reactor_small

    is_action_valid = equip_iav

class ElementalReactorSkill:
    # Skill
    name = u'八卦炉'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class UmbrellaCard:
    # action_stage meta
    name = u'紫的阳伞'
    image = gres.card_umbrella
    image_small = gres.card_umbrella_small

    is_action_valid = equip_iav

class UmbrellaSkill:
    # Skill
    name = u'紫的阳伞'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class RoukankenCard:
    # action_stage meta
    name = u'楼观剑'
    image = gres.card_roukanken
    image_small = gres.card_roukanken_small

    is_action_valid = equip_iav

class RoukankenSkill:
    # Skill
    name = u'楼观剑'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class RoukankenHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【楼观剑】吗？'

class Roukanken:
    def effect_string_before(act):
        return (
            u'虽然上一刀落空了，但是|G楼观剑|r的气势并未褪去。' +
            u'|G【%s】|r调整了姿势，再次向|G【%s】|r出刀！'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,

        )

class GungnirCard:
    # action_stage meta
    name = u'冈格尼尔'
    image = gres.card_gungnir
    image_small = gres.card_gungnir_small

    is_action_valid = equip_iav

class GungnirSkill:
    # Skill
    name = u'冈格尼尔'

    def clickable(game):
        me = game.me
        try:
            act = game.action_stack[0]
            if isinstance(act, (actions.ActionStage, cards.UseAttack, cards.DollControl)):
                return True
        except IndexError:
            pass
        return False

    def is_complete(g, cl):
        skill = cl[0]
        me = g.me
        assert skill.is_card(cards.GungnirSkill)
        acards = skill.associated_cards
        if len(acards) != 2:
            return (False, u'请选择2张手牌！')
        elif any(c.resides_in not in (me.cards, me.showncards) for c in acards):
            return (False, u'只能使用手牌发动！')
        return (True, u'反正这条也看不到，偷个懒~~~')

    def is_action_valid(g, cl, target_list, is_complete=is_complete):
        skill = cl[0]
        assert skill.is_card(cards.GungnirSkill)
        rst, reason = is_complete(g, cl)
        if not rst:
            return (rst, reason)
        else:
            return cards.AttackCard.ui_meta.is_action_valid(g, [skill], target_list)

    def effect_string(act):
        # for LaunchCard.effect_string
        source = act.source
        card = act.card
        target = act.target_list[0]
        s = u'|G【%s】|r发动了|G冈格尼尔|r之枪，将两张牌当作|G弹幕|r对|G【%s】|r使用。' % (
            source.ui_meta.char_name,
            target.ui_meta.char_name,
        )
        return s

class LaevateinCard:
    # action_stage meta
    name = u'莱瓦汀'
    image = gres.card_laevatein
    image_small = gres.card_laevatein_small

    is_action_valid = equip_iav

class LaevateinSkill:
    # Skill
    name = u'莱瓦汀'

    def clickable(game):
        me = game.me
        try:
            act = game.action_stack[0]
            if isinstance(act, actions.ActionStage):
                cl = list(me.cards) + list(me.showncards)
                if len(cl) == 1 and isinstance(cl[0], cards.AttackCard):
                    return True
        except IndexError:
            pass
        return False

    def is_action_valid(g, cl, target_list):
        skill = cl[0]
        assert skill.is_card(cards.LaevateinSkill)
        acards = skill.associated_cards
        if not (len(acards) == 1 and acards[0].is_card(cards.AttackCard)):
            return (False, u'请选择你的最后一张【弹幕】！')
        else:
            if not target_list:
                return (False, u'请选择弹幕的目标（最多可以选择3名玩家）')

            if g.me in target_list:
                return (True, u'您真的要自残么？！')
            else:
                return (True, u'觉醒吧，禁忌的炎之魔剑！')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        source = act.source
        card = act.card
        tl = BatchList(act.target_list)

        return u'|G【%s】|r不顾危险发动了|G莱瓦汀|r，火焰立刻扑向了对|G【%s】|r！' % (
            s.ui_meta.char_name,
            u'】|r、|G【'.join(tl.ui_meta.char_name),
        )

class TridentCard:
    # action_stage meta
    name = u"三叉戟"
    image = gres.card_trident
    image_small = gres.card_trident_small

    is_action_valid = equip_iav

class TridentSkill:
    # Skill
    name = u"三叉戟"

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class RepentanceStickCard:
    # action_stage meta
    name = u'悔悟棒'
    image = gres.card_repentancestick
    image_small = gres.card_repentancestick_small

    is_action_valid = equip_iav

class RepentanceStickSkill:
    # Skill
    name = u'悔悟棒'
    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class RepentanceStickHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【悔悟棒】吗？'

class RepentanceStick:
    def effect_string_before(act):
        return (
            u'|G【%s】|r用|G悔悟棒|r狠狠的敲了|G【%s】|r一通…'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,

        )

    def effect_string(act):
        cl = BatchList(act.cards)
        return u'又抢过|G【%s】|r的|G%s|r扔了出去！' % (
            act.target.ui_meta.char_name,
            u'|r和|G'.join(cl.ui_meta.name)
        )

class FeastCard:
    # action_stage meta
    image = gres.card_feast
    name = u'宴会'

    def is_action_valid(g, cl, target_list):
        return (True, u'开宴啦~~')

class HarvestCard:
    # action_stage meta
    image = gres.card_harvest
    name = u'五谷丰登'

    def is_action_valid(g, cl, target_list):
        return (True, u'麻薯会有的，节操是没有的！')

class HarvestEffect:
    def effect_string(act):
        if not act.succeeded: return None
        tgt = act.target
        c = act.card
        return u'|G【%s】|r获得了|G%s|r' % (
            tgt.ui_meta.char_name,
            c.ui_meta.name,
        )

class MaidenCostumeCard:
    # action_stage meta
    name = u'巫女服'
    image = gres.card_maidencostume
    image_small = gres.card_maidencostume_small

    def is_action_valid(g, cl, target_list):
        if not target_list:
            return (False, u'请选择目标')
        t = target_list[0]
        if g.me is t:
            return (True, u'真的要自己穿上吗？')
        return (True, u'\腋/！')

class MaidenCostumeSkill:
    # Skill
    name = u'巫女服'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class IbukiGourdCard:
    # action_stage meta
    name = u'伊吹瓢'
    image = gres.card_ibukigourd
    image_small = gres.card_ibukigourd_small
    is_action_valid = equip_iav

class IbukiGourdSkill:
    # Skill
    name = u'伊吹瓢'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class HouraiJewelCard:
    # action_stage meta
    name = u'蓬莱玉枝'
    image = gres.card_houraijewel
    image_small = gres.card_houraijewel_small
    is_action_valid = equip_iav

class HouraiJewelSkill:
    # Skill
    name = u'蓬莱玉枝'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class HouraiJewelHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【蓬莱玉枝】吗？'

class HouraiJewelAttack:
    def effect_string_before(act):
        return (
            u'|G【%s】|r发动了|G蓬莱玉枝|r，包裹着魔法核心的弹幕冲向了|G【%s】|r！'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class SaigyouBranchCard:
    # action_stage meta
    name = u'西行妖枝条'
    image = gres.card_saigyoubranch
    image_small = gres.card_saigyoubranch_small
    is_action_valid = equip_iav

class SaigyouBranchSkill:
    # Skill
    name = u'西行妖枝条'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class SaigyouBranchHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【西行妖枝条】吗？'

class SaigyouBranch:
    def effect_string_before(act):
        return (
            u'|G西行妖|r的枝条受到了|G【%s】|r春度的滋养，' +
            u'在关键时刻突然撑出一片结界，试图将符卡挡下！'
        ) % (
            act.source.ui_meta.char_name,
        )

    def effect_string(act):
        if not act.succeeded:
            return (
                u'但是很明显|G【%s】|r的春度不够用了…'
            ) % (
                act.source.ui_meta.char_name,
            )

class FlirtingSwordCard:
    # action_stage meta
    name = u'调教剑'
    image = gres.card_flirtingsword
    image_small = gres.card_flirtingsword_small
    is_action_valid = equip_iav

class FlirtingSwordSkill:
    # Skill
    name = u'调教剑'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class FlirtingSword:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【调教剑】吗？'

    # choose_card
    text_valid = u'才……才不给你机会呢！'
    text = u'请弃掉一张牌（否则对方摸一张牌）'

    def effect_string_before(act):
        return (
            u'|G【%s】|r拿起了|G调教剑|r，对着|G【%s】|r做起了啪啪啪的事！'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

    def effect_string(act):
        if act.peer_action == 'drop':
            return (
                u'但是|G【%s】|r不太情愿，拿起一张牌甩在了|G【%s】|r的脸上！'
            ) % (
                act.target.ui_meta.char_name,
                act.source.ui_meta.char_name,
            )
        else:
            return (
                u'|G【%s】|r被（哗）后，|G【%s】|r居然摆着人生赢家的姿态摸了一张牌！'
            ) % (
                act.target.ui_meta.char_name,
                act.source.ui_meta.char_name,
            )

class CameraCard:
    # action_stage meta
    name = u'文文的相机'
    image = gres.card_camera

    def is_action_valid(g, cl, tl):
        if not tl:
            return (False, u'请选择目标')
        t = tl[0]

        if not t.cards:
            return (True, u'这货已经没有隐藏的手牌了')

        return (True, u'摄影的境界，你们这些玩器材的永远都不会懂！')

class AyaRoundfanCard:
    # action_stage meta
    name = u'文文的团扇'
    image = gres.card_ayaroundfan
    image_small = gres.card_ayaroundfan_small
    is_action_valid = equip_iav

class AyaRoundfanSkill:
    # Skill
    name = u'文文的团扇'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class AyaRoundfanHandler:
    # choose_card
    text_valid = u'这种妨碍拍摄的东西，统统脱掉！'
    text = u'请弃掉一张手牌发动团扇（否则不发动）'

class AyaRoundfan:
    def effect_string_before(act):
        return (
            u'|G【%s】|r觉得手中的|G团扇|r用起来好顺手，便加大力度试了试…'
        ) % (
            act.source.ui_meta.char_name,
        )

    def effect_string(act):
        return (
            u'于是|G【%s】|r的|G%s|r就飞了出去！'
        ) % (
            act.target.ui_meta.char_name,
            act.card.ui_meta.name,
        )

class ScarletRhapsodySwordCard:
    # action_stage meta
    name = u'绯想之剑'
    image = gres.card_scarletrhapsodysword
    image_small = gres.card_scarletrhapsodysword_small
    is_action_valid = equip_iav

class ScarletRhapsodySwordSkill:
    # Skill
    name = u'绯想之剑'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class ScarletRhapsodySwordHandler:
    # choose_card
    text_valid = u'闪过头了！'
    text = u'请弃掉两张牌发动绯想之剑（否则不发动）'

class ScarletRhapsodySword:
    def effect_string_before(act):
        sn, tn = act.source.ui_meta.char_name, act.target.ui_meta.char_name
        return (
            u'但是弱点早已被|G绯想之剑|r看穿，在|G【%s】|r还未' +
            u'停稳脚步时，|G【%s】|r给了她精准的一击！'
        ) % (
            tn, sn
        )

class DeathSickleCard:
    # action_stage meta
    name = u'死神之镰'
    image = gres.card_deathsickle
    image_small = gres.card_deathsickle_small
    is_action_valid = equip_iav

class DeathSickleSkill:
    # Skill
    name = u'死神之镰'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class DeathSickle:
    def effect_string(act):
        return (
            u'|G【%s】|r看到|G【%s】|r一副丧家犬的模样，' +
            '手中的|c208020f死神之镰|r不自觉地一狠…'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class KeystoneCard:
    # action_stage meta
    name = u'要石'
    image = gres.card_keystone
    image_small = gres.card_keystone_small
    is_action_valid = equip_iav

class KeystoneSkill:
    # Skill
    name = u'要石'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class Keystone:
    def effect_string(act):
        return u'|G【%s】|r站在|G要石|r上，照着|G罪袋|r的脸一脚踹了下去！' % (
            act.target.ui_meta.char_name
        )

class WitchBroomCard:
    # action_stage meta
    name = u'魔女的扫把'
    image = gres.card_witchbroom
    image_small = gres.card_witchbroom_small
    is_action_valid = equip_iav

class WitchBroomSkill:
    # Skill
    no_display = True

class YinYangOrbCard:
    # action_stage meta
    name = u'阴阳玉'
    image = gres.card_yinyangorb
    image_small = gres.card_yinyangorb_small
    is_action_valid = equip_iav

class YinYangOrbSkill:
    # Skill
    name = u'阴阳玉'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class YinYangOrbHandler:
    # choose_option
    choose_option_buttons = ((u'替换', True), (u'不替换', False))
    choose_option_prompt = u'你要使用【阴阳玉】替换当前的判定牌吗？'

class YinYangOrb:
    def effect_string(act):
        return (
            u'|G【%s】|r用|G阴阳玉|r代替了她的判定牌'
        ) % (
            act.target.ui_meta.char_name,
        )

class SuwakoHatCard:
    # action_stage meta
    name = u'青蛙帽'
    image = gres.card_suwakohat
    image_small = gres.card_suwakohat_small
    is_action_valid = equip_iav

class SuwakoHatSkill:
    # Skill
    name = u'青蛙帽'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class YoumuPhantomCard:
    # action_stage meta
    name = u'半灵'
    image = gres.card_phantom
    image_small = gres.card_phantom_small
    is_action_valid = equip_iav

class YoumuPhantomSkill:
    # Skill
    name = u'半灵'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class IceWingCard:
    # action_stage meta
    name = u'⑨的翅膀'
    image = gres.card_icewing
    image_small = gres.card_icewing_small
    is_action_valid = equip_iav

class IceWingSkill:
    # Skill
    name = u'⑨的翅膀'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class IceWing:
    def effect_string(act):
        return u'|G【%s】|r借着|G⑨的翅膀|r飞了出来，|G封魔阵|r没起到什么作用' % (
            act.target.ui_meta.char_name
        )

class GrimoireCard:
    # action_stage meta
    name = u'魔导书'
    image = gres.card_grimoire
    image_small = gres.card_grimoire_small

    is_action_valid = equip_iav

class GrimoireSkill:
    # Skill
    name = u'魔导书'

    def clickable(game):
        me = game.me
        try:
            act = game.action_stack[0]
            if isinstance(act, actions.ActionStage):
                if me.tags.get('attack_num', 0):
                    return True
        except IndexError:
            pass
        return False

    def is_action_valid(g, cl, target_list):
        skill = cl[0]
        assert skill.is_card(cards.GrimoireSkill)
        acards = skill.associated_cards
        if not (len(acards)) == 1:
            return (False, u'请选择一张牌')
        else:
            s = skill.lookup_tbl[acards[0].suit].ui_meta.name
            return (True, u'发动【%s】' % s)

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        source = act.source
        card = act.card
        return (
            u'|G【%s】|r抓起一张牌放入|G魔导书|r' +
            u'，念动咒语，发动了|G%s|r。'
        ) % (
            source.ui_meta.char_name,
            card.lookup_tbl[card.associated_cards[0].suit].ui_meta.name
        )

class DollControlCard:
    # action_stage meta
    name = u'人形操控'
    image = gres.card_dollcontrol

    def is_action_valid(g, cl, tl):
        n = len(tl)
        if n == 0:
            return (False, u'请选择被控者')

        if tl[0] is g.me:
            return (False, u'你不可以控制你自己')

        if all(e.equipment_category != 'weapon' for e in tl[0].equips):
            return (False, u'被控者没有武器！')

        if n == 1:
            return (False, u'请选择被控者的攻击目标')
        elif n == 2:
            from .. import actions, cards
            c = cards.AttackCard()
            lc = actions.LaunchCard(tl[0], [tl[1]], c)
            if not lc.can_fire():
                return (False, u'被控者无法向目标出【弹幕】！')
            return (True, u'乖，听话！')

class DollControl:
    # choose card meta
    text_valid = u'那好吧…'
    text = u'请出【弹幕】（否则你的武器会被拿走）'

class DonationBoxCard:
    # action_stage meta
    name = u'塞钱箱'
    image = gres.card_donationbox

    def is_action_valid(g, cl, tl):
        n = len(tl)
        if not n:
            return (False, u'请选择1-2名玩家')

        if g.me in tl:
            return (False, u'你不能选择自己作为目标')

        for t in tl:
            if not (t.cards or t.showncards or t.equips):
                return (False, u'目标没有可以给你的牌')

        return (True, u'纳奉！纳奉！')

class DonationBox:
    # choose card meta
    text_valid = u'这是抢劫啊！'
    text = u'请选择一张牌（否则会随机选择一张）'

# -----END CARDS UI META-----

# -----BEGIN CHARACTERS UI META-----
__metaclass__ = gen_metafunc(characters)

class Parsee:
    # Character
    char_name = u'水桥帕露西'
    port_image = gres.parsee_port

class Envy:
    # Skill
    name = u'嫉妒'

    def clickable(game):
        me = game.me

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards or me.equips):
            return True

        return False

    def is_action_valid(g, cl, target_list):
        skill = cl[0]
        assert skill.is_card(characters.Envy)
        cl = skill.associated_cards
        if len(cl) != 1:
            return (False, u'请选择一张牌！')
        else:
            c = cl[0]
            if c.suit not in (cards.Card.SPADE, cards.Card.CLUB):
                return (False, u'请选择一张黑色的牌！')
            return cards.DemolitionCard.ui_meta.is_action_valid(g, [skill], target_list)

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        source = act.source
        card = act.card
        target = act.target_list[0]
        s = u'|G【%s】|r发动了嫉妒技能，将|G%s|r当作|G%s|r对|G【%s】|r使用。' % (
            source.ui_meta.char_name,
            card.associated_cards[0].ui_meta.name,
            card.treat_as.ui_meta.name,
            target.ui_meta.char_name,
        )
        return s

# ----------

class Youmu:
    # Character
    char_name = u'魂魄妖梦'
    port_image = gres.youmu_port

class Mijincihangzhan:
    # Skill
    name = u'迷津慈航斩'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

# ----------

class Koakuma:
    # Character
    char_name = u'小恶魔'
    port_image = gres.koakuma_port

class Find:
    # Skill
    name = u'寻找'

    def clickable(game):
        me = game.me
        if me.tags.get('find_tag', 0) >= me.tags.get('turn_count', 0):
            return False

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards or me.equips):
            return True

        return False

    def is_action_valid(g, cl, target_list):
        skill = cl[0]
        assert skill.is_card(characters.Find)
        if not len(skill.associated_cards):
            return (False, u'请选择需要换掉的牌！')

        if not [g.me] == target_list:
            return (False, 'BUG!!')

        return (True, u'换掉这些牌')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        source = act.source
        card = act.card
        target = act.target_list[0]
        s = u'|G【%s】|r发动了寻找技能，换掉了%d张牌。' % (
            source.ui_meta.char_name,
            len(card.associated_cards),
        )
        return s

# ----------

class Marisa:
    # Character
    char_name = u'雾雨魔理沙'
    port_image = gres.marisa_port

class Borrow:
    # Skill
    name = u'借走'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class BorrowHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【借走】技能吗？'

    # choose_players
    def target(pl):
        if not pl:
            return (False, u'请选择1-2名玩家')

        return (True, u'哎哎，什么还不还的~')

class BorrowAction:
    def effect_string(act):
        return u'大盗|G【%s】|r又跑出来“|G借走|r”了|G【%s】|r的牌。' % (
            act.source.ui_meta.char_name,
            u'】|r和|G【'.join(BatchList(act.target_list).ui_meta.char_name),
        )

# ----------

class Daiyousei:
    # Character
    char_name = u'大妖精'
    port_image = gres.daiyousei_port

class SupportSkill:
    # Skill
    name = u'支援'

    def clickable(game):
        me = game.me

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards or me.equips):
            return True

        return False

    def is_action_valid(g, cl, target_list):
        cl = cl[0].associated_cards
        if not cl: return (False, u'请选择要给出的牌')
        if len(target_list) != 1: return (False, u'请选择1名玩家')
        return (True, u'加油！')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return u'|G【%s】|r发动了|G支援|r技能，将%d张手牌交给了|G【%s】|r' % (
            act.source.ui_meta.char_name,
            len(act.cards),
            act.target.ui_meta.char_name,
        )

class Moe:
    # Skill
    name = u'卖萌'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class MoeDrawCard:
    def effect_string(act):
        return u'|G【%s】|r用手扯开脸颊，向大家做了一个夸张的笑脸，摸了%d张牌跑开了' % (
            act.target.ui_meta.char_name,
            act.amount,
        )

# ----------

class Flandre:
    # Character
    char_name = u'芙兰朵露'
    port_image = gres.flandre_port

class CriticalStrike:
    # Skill
    name = u'狂咲'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class CriticalStrikeHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【狂咲】吗？'

class CriticalStrikeAction:
    def effect_string(act):
        return u'|G【%s】|r突然呵呵一笑，进入了黑化状态！' % (
            act.target.ui_meta.char_name,
        )

# ----------

class Alice:
    # Character
    char_name = u'爱丽丝'
    port_image = gres.alice_port

class DollManipulation:
    # Skill
    name = u'人形操演'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

# ----------

class Nazrin:
    # Character
    char_name = u'娜兹琳'
    port_image = gres.nazrin_port

class TreasureHuntSkill:
    # Skill
    name = u'探宝'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class TreasureHuntHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【探宝】吗？'

class Agile:
    # Skill
    name = u'轻敏'

    def clickable(game):
        me = game.me

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, cards.UseGraze) and (me.cards or me.showncards):
            return True

        return False

    def is_complete(g, cl):
        skill = cl[0]
        cl = skill.associated_cards
        if len(cl) != 1:
            return (False, u'请选择一张牌！')
        else:
            c = cl[0]
            if c.suit not in (cards.Card.SPADE, cards.Card.CLUB):
                return (False, u'请选择一张黑色的牌！')
            return (True, u'这种三脚猫的弹幕，想要打中我是不可能的啦~')

class TreasureHunt:
    def effect_string(act):
        if act.succeeded:
            return u'|G【%s】|r找到了一张|G%s|r' % (
                act.target.ui_meta.char_name,
                act.card.ui_meta.name,
            )
        else:
            return u'|G【%s】|r什么也没有找到…' % (
                act.target.ui_meta.char_name,
            )

# ----------

class Yugi:
    # Character
    char_name = u'星熊勇仪'
    port_image = gres.yugi_port

class AssaultSkill:
    # Skill
    name = u'强袭'

    def clickable(game):
        me = game.me
        if me.tags.get('yugi_assault', 0) >= me.tags.get('turn_count', 0):
            return False
        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        return isinstance(act, actions.ActionStage)

    def is_action_valid(g, cl, target_list):
        if not target_list:
            return (False, u'请选择强袭的目标，以及一张武器牌（不选自己会受到1点伤害）')

        if g.me is target_list[0]:
            return (False, u'不可以对自己发动')
        else:
            return (True, u'[不知道该说什么，先这样吧]')

    def effect_string(act):
        return u'|G【%s】|r向|G【%s】|r发动了|G强袭|r技能' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name
        )

class FreakingPowerSkill:
    # Skill
    name = u'怪力'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class FreakingPower:
    def effect_string_before(act):
        return u'|G【%s】|r稍微认真了一下，弹幕以惊人的速度冲向|G【%s】|r' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class YugiHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【怪力】吗？'

# ----------

class Library:
    # Skill
    name = u'图书'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class LibraryDrawCards:
    def effect_string(act):
        return u'|G【%s】|r发动了|G图书|r技能，摸1张牌。' % (
            act.source.ui_meta.char_name,
        )

class Knowledge:
    # Skill
    name = u'博学'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class KnowledgeAction:
    def effect_string(act):
        return u'|G【%s】|r一眼就看穿了这张符卡，直接被挡下了。' % (
            act.source.ui_meta.char_name,
        )

class Patchouli:
    # Character
    char_name = u'帕秋莉'
    port_image = gres.patchouli_port

# ----------

class Luck:
    # Skill
    name = u'幸运'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class LuckDrawCards:
    def effect_string(act):
        return u'|G【%s】|r觉得手上没有牌就输了，于是又摸了2张牌。' % (
            act.source.ui_meta.char_name,
        )

class Tewi:
    # Character
    char_name = u'因幡帝'
    port_image = gres.tewi_port

# ----------

class SealingArraySkill:
    # Skill
    name = u'封魔阵'
    image = gres.card_sealarray
    tag_anim = gres.tag_sealarray

    def clickable(game):
        me = game.me

        if me.tags.get('reimusa_tag', 0) >= me.tags.get('turn_count', 0):
            return False

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards or me.equips):
            return True

        return False

    def is_action_valid(g, cl, target_list):
        skill = cl[0]
        cl = skill.associated_cards
        if len(cl) != 1:
            return (False, u'请选择一张牌！')
        else:
            c = cl[0]
            if c.suit != cards.Card.DIAMOND:
                return (False, u'请选择一张方片花色的牌！')
            return (True, u'乖，歇会吧~')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        source = act.source
        card = act.card
        target = act.target_list[0]
        return (
            u'|G【%s】|r发动了|G封魔阵|r技能，用|G%s|r' +
            u'在|G【%s】|r的脚下画了一个大圈圈！'
        ) % (
            source.ui_meta.char_name,
            card.associated_cards[0].ui_meta.name,
            target.ui_meta.char_name,
        )

class Flight:
    # Skill
    name = u'飞行'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class TributeTarget:
    # Skill
    name = u'纳奉'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class Tribute:
    # Skill
    name = u'塞钱'

    def clickable(game):
        me = game.me

        if me.tags.get('tribute_tag', 0) >= me.tags.get('turn_count', 0):
            return False

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards or me.equips):
            return True

        return False

    def is_action_valid(g, cl, tl):
        cl = cl[0].associated_cards
        if not cl: return (False, u'请选择要给出的牌')
        if len(cl) != 1: return (False, u'只能选择一张牌')
        if len(tl) != 1 or not tl[0].has_skill(characters.TributeTarget):
            return (False, u'请选择一只灵梦')
        return (True, u'塞钱……会发生什么呢？')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return (
            u'|G【%s】|r向|G【%s】|r的塞钱箱里放了一张牌… 会发生什么呢？'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )


class Reimu:
    # Character
    char_name = u'博丽灵梦'
    port_image = gres.reimu_port

# ----------

class Jolly:
    # Skill
    name = u'愉快'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class SurpriseSkill:
    # Skill
    name = u'惊吓'

    def clickable(game):
        me = game.me

        if me.tags.get('surprise_tag', 0) >= me.tags.get('turn_count', 0):
            return False

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards):
            return True

        return False

    def is_action_valid(g, cl, tl):
        if len(tl) != 1:
            return (False, u'请选择惊吓对象…')
        #return (True, u'(´・ω・`)')
        return (True, u'\ ( °▽ °) /')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return (
            u'|G【%s】|r突然出现在|G【%s】|r面前，伞上' +
            u'的大舌头直接糊在了|G【%s】|r的脸上！'
        ) % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class Surprise:
    # choose_option
    choose_option_buttons = (
        (u'黑桃', cards.Card.SPADE),
        (u'红桃', cards.Card.HEART),
        (u'草花', cards.Card.CLUB),
        (u'方片', cards.Card.DIAMOND),
    )
    choose_option_prompt = u'请选择一个花色…'

    def effect_string(act):
        if act.succeeded:
            return u'效果拔群！'
        else:
            return u'似乎没有什么效果'

class Kogasa:
    # Character
    char_name = u'多多良小伞'
    port_image = gres.kogasa_port

# ----------

class FirstAid:
    # Skill
    name = u'急救'

    def clickable(game):
        me = game.me

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, cards.UseHeal):
            return True

        return False

    def is_complete(g, cl):
        skill = cl[0]
        me = g.me
        acards = skill.associated_cards
        if len(acards) != 1:
            return (False, u'请选择一张红色牌！')
        return (True, u'k看不到@#@#￥@#￥')

class Medic:
    # Skill
    name = u'医者'

    def clickable(game):
        me = game.me

        if me.tags.get('turn_count', 0) <= me.tags.get('medic_tag', 0):
            return False

        try:
            act = game.action_stack[0]
        except IndexError:
            return False

        if isinstance(act, actions.ActionStage) and (me.cards or me.showncards):
            return True

        return False

    def is_action_valid(g, cl, tl):
        skill = cl[0]
        me = g.me
        cl = skill.associated_cards
        if len(cl) != 1:
            return (False, u'请选择一张手牌！')
        elif any(c.resides_in not in (me.cards, me.showncards) for c in cl):
            return (False, u'只能使用手牌发动！')
        elif not tl or len(tl) != 1:
            return (False, u'请选择一名受伤的玩家')
        elif tl[0].maxlife <= tl[0].life:
            return (False, u'这只精神着呢，不用管她')
        return (True, u'少女，身体要紧啊！')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return (
            u'|G【%s】|r用一张|G%s|r做药引做了一贴膏药，' +
            u'细心地贴在了|G【%s】|r的伤口上。'
        ) % (
            act.source.ui_meta.char_name,
            act.card.associated_cards[0].ui_meta.name,
            act.target.ui_meta.char_name,
        )

class Eirin:
    # Character
    char_name = u'八意永琳'
    port_image = gres.eirin_port

# ----------

class Trial:
    # Skill
    name = u'审判'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class TrialAction:
    def effect_string(act):
        return u'幻想乡各地巫女妖怪纷纷表示坚决拥护|G【%s】|r修改|G【%s】|r判定结果的有关决定！' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class Majesty:
    # Skill
    name = u'威严'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class MajestyAction:
    def effect_string(act):
        return u'|G【%s】|r脸上挂满黑线，收走了|G【%s】|r的一张牌作为罚款' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class TrialHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【审判】吗？'

    # choose_card
    text = u'请选择一张牌代替当前的判定牌'
    text_valid = u'有罪！'

class MajestyHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【威严】吗？'

class Shikieiki:
    # Character
    char_name = u'四季映姬'
    port_image = gres.shikieiki_port

# ----------

class Masochist:
    # Skill
    name = u'抖Ｍ'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class MasochistHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【抖Ｍ】吗？'

class MasochistAction:
    # choose_card
    text = u'请选择你要给出的牌'
    text_valid = u'给你牌~'

    def target(pl):
        if not pl:
            return (False, u'请选择1名玩家')

        return (True, u'给你牌~')

    def effect_string_before(act):
        return u'不过|G【%s】|r好像很享受的样子…' % (
            act.target.ui_meta.char_name,
        )

class Tenshi:
    # Character
    char_name = u'比那名居天子'
    port_image = gres.tenshi_port

# ----------

class FlowerQueen:
    # Skill
    name = u'花王'

    def clickable(game):
        me = game.me
        try:
            act = game.action_stack[0]
            if isinstance(act, (actions.ActionStage, cards.UseAttack, cards.UseGraze, cards.DollControl)):
                return True
        except IndexError:
            pass
        return False

    def is_complete(g, cl):
        skill = cl[0]
        me = g.me
        acards = skill.associated_cards
        if len(acards) != 1 or acards[0].suit != cards.Card.CLUB:
            return (False, u'请选择1张草花色手牌！')
        return (True, u'反正这条也看不到，偷个懒~~~')

    def is_action_valid(g, cl, target_list, is_complete=is_complete):
        skill = cl[0]
        rst, reason = is_complete(g, cl)
        if not rst:
            return (rst, reason)
        else:
            return cards.AttackCard.ui_meta.is_action_valid(g, [skill], target_list)

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return None # FIXME

class MagicCannon:
    # Skill
    name = u'魔炮'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class MagicCannonAttack:
    def effect_string(act):
        return (
            u'|G【%s】|r已经做好了迎接弹幕的准备，谁知冲过来的竟是一束|G魔炮|r！'
        ) % (
            act.target.ui_meta.char_name,
        )

class PerfectKill:
    # Skill
    name = u'完杀'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class PerfectKillAction:
    def effect_string(act):
        return (
            u'在场的人无不被|G【%s】|r的气场镇住，竟连上前递|G麻薯|r的勇气都没有了！'
        ) % (
            act.source.ui_meta.char_name,
        )

class Yuuka:
    # Character
    char_name = u'风见幽香'
    port_image = gres.yuuka_port

# ----------

class Darkness:
    # Skill
    name = u'黑暗'

    def clickable(game):
        me = game.me
        try:
            tags = me.tags
            if tags['turn_count'] <= tags['darkness_tag']:
                return False
            act = game.action_stack[0]
            if isinstance(act, actions.ActionStage):
                return True
        except IndexError:
            pass
        return False

    def is_action_valid(g, cl, tl):
        skill = cl[0]
        cl = skill.associated_cards
        if not cl or len(cl) != 1:
            return (False, u'请选择一张牌')

        if not len(tl):
            return (False, u'请选择第一名玩家（先出弹幕）')
        elif len(tl) == 1:
            return (False, u'请选择第二名玩家（后出弹幕）')
        else:
            return (True, u'你们的关系…是~这样吗？')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return u'|G【%s】|r在黑暗中一通乱搅，结果|G【%s】|和|G【%s】|打了起来！' % (
            act.source.ui_meta.char_name,
            act.target_list[0].ui_meta.char_name,
            act.target_list[1].ui_meta.char_name,
        )

class Cheating:
    # Skill
    name = u'作弊'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class CheatingDrawCards:
    def effect_string(act):
        return u'突然不知道是谁把太阳挡住了。等到大家回过神来，赫然发现牌堆里少了一张牌！'

class Rumia:
    # Character
    char_name = u'露米娅'
    port_image = gres.rumia_port

# ----------

class Netoru:
    # Skill
    name = u'寝取'

    def clickable(game):
        me = game.me
        try:
            if me.tags['netoru_tag'] >= me.tags['turn_count']:
                return False
            act = game.action_stack[0]
            if isinstance(act, actions.ActionStage):
                return True
        except IndexError:
            pass
        return False

    def is_action_valid(g, cl, tl):
        skill = cl[0]
        cl = skill.associated_cards
        me = g.me
        if not cl or len(cl) != 2:
            return (False, u'请选择两张手牌')
        elif any(c.resides_in not in (me.cards, me.showncards) for c in cl):
            return (False, u'只能使用手牌发动！')

        if len(tl) != 1:
            return (False, u'请选择一名受伤的玩家')

        t = tl[0]
        if t.life >= t.maxlife:
            return (False, u'这位少女节操满满，不会答应你的…')
        else:
            return (True, u'少女，做个好梦~')

    def effect_string(act):
        # for LaunchCard.ui_meta.effect_string
        return u'|G【%s】|r一改平日的猥琐形象，竟然用花言巧语将|G【%s】|r骗去啪啪啪了！' % (
            act.source.ui_meta.char_name,
            act.target.ui_meta.char_name,
        )

class Psychopath:
    # Skill
    name = u'变态'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class PsychopathDrawCards:
    def effect_string(act):
        return (
            u'|G【%s】|r满脸猥琐地将装备脱掉，结果众人抄起了%d张牌糊在了他身上。'
        ) % (
            act.target.ui_meta.char_name,
            act.amount,
        )

class Rinnosuke:
    # Character
    char_name = u'森近霖之助'
    port_image = gres.rinnosuke_port

# ----------

class Fengshui:
    # Skill
    name = u'风水'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class ExtremeIntelligence:
    # Skill
    name = u'极智'

    def clickable(game):
        return False

    def is_action_valid(g, cl, target_list):
        return (False, 'BUG!')

class FengshuiHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【风水】吗？'

class FengshuiAction:
    def effect_string_before(act):
        return u'众人正准备接招呢，|G【%s】|r却不急不忙地看起了|G风水|r…' % (
            act.target.ui_meta.char_name,
        )

class ExtremeIntelligenceHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【极智】吗？'

class ExtremeIntelligenceAction:
    # choose_card
    text = u'请选择1张牌弃置'
    text_valid = u'再来！'

    def effect_string(act):
        return (
            u'|G【%s】|r刚松了一口气，却看见一张一模一样的符卡从|G【%s】|r的方向飞来！'
        ) % (
            act.target.ui_meta.char_name,
            act.source.ui_meta.char_name,
        )

class Ran:
    # Character
    char_name = u'八云蓝'
    port_image = gres.ran_port

# -----END CHARACTERS UI META-----

# -----BEGIN TAGS UI META-----
tags = {}
def tag_metafunc(clsname, bases, _dict):
    data = DataHolder.parse(_dict)
    tags[clsname] = data

__metaclass__ = tag_metafunc

class attack_num:
    tag_anim = gres.tag_attacked
    display = lambda val: val <= 0

class wine:
    tag_anim = gres.tag_wine
    display = lambda val: val
# -----END TAGS UI META-----
