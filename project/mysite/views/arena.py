from mysite.models import UserCustomWord, Word, WordDeutch, UserWordsProgress, UserWordsDeutchProgress, User, UserSettings, WordCategory, WordSubcategory, PlayerProfile, Battle, BossProfile, Skill, PlayerSkill, BossSkill, BattleTurn, BattleRound
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
import json
from django.views.decorators.http import require_POST


from .utils import get_all_info
#==================================================================================== ARENA PAGE ==========================================================================================
@login_required
def arena_page(request):
    return render(request, 'arena.html', context = {'page_name': 'arena',
                                                    'user_info': get_all_info(request.user),})

def serialize_battle(battle):
    result = {'battle_id': battle.id,
              'battle_status': battle.battle_status,
            'round_number': battle.round_number,
            'round_status': battle.round_status}
    if battle.player_1:
        result['player_1'] = {
                'name': battle.player_1.name,
                'hitpoints': battle.player_1.hitpoints,
                'mana': battle.player_1.mana,
                'endurance': battle.player_1.endurance,
                'skills': list(battle.player_1.skills.values_list('skill_id', flat=True))
            }
    if battle.player_2:
        result['player_2'] = {
                'name': battle.player_2.name,
                'hitpoints': battle.player_2.hitpoints,
                'mana': battle.player_2.mana,
                'endurance': battle.player_2.endurance,
                'skills': list(battle.player_2.skills.values_list('skill_id', flat=True))
            }
    if battle.boss:
        result['boss'] = {
            'name': battle.boss.name,
            'level': battle.boss.level,
            'hitpoints': battle.boss.hitpoints,
            'mana': battle.boss.mana,
            'endurance': battle.boss.endurance,
        }
    return result

# ----------------------------------------------------------------------- FIND BATTLE
BATTLE_STATUS_WAITING_PLAYER_2 = 1  # Битва створена, PLAYER_1 READY
BATTLE_STATUS_PROCESS = 2  # PLAYER 2 READY
BATTLE_STATUS_PENDING = 3
BATTLE_STATUS_FINISHED = 4

@login_required
def find_pvp_battle(request):
    player = request.user.player_profile
    # boss = BossProfile.objects.get(name='TEST_BOSS')

    battle_player_1 = Battle.objects.filter(
        battle_type = 'PVP',
        is_active = True,
        player_1 = player,
    ).first()

    if battle_player_1 :
        print( '--->>> BATTLE_PLAYER_! TRUE')
        return JsonResponse({
        'status': 'OK',
        'player_status': 'player_1',
        'battle_info': serialize_battle(battle_player_1)      
    })
    
    battle_player_2 = Battle.objects.filter(
        battle_type = 'PVP',
        is_active = True,
        player_2 = player,
    ).first()

    if battle_player_2:
        return JsonResponse({
        'status': 'OK',
        'player_status': 'player_2',
        'battle_info': serialize_battle(battle_player_2)      
    })
    
     # NO BATTLE AT ALL -> FIND OPEN BATTLE OR CREATE NEW BATTLE
    if not battle_player_1 and not battle_player_2:

         # шукаємо битву без другого гравця
        open_battle = Battle.objects.filter(
            battle_type='PVP',
            is_active=True,
            battle_status=BATTLE_STATUS_WAITING_PLAYER_2,
            player_2__isnull=True
        ).exclude(player_1=player).first()

        if open_battle:
            open_battle.player_2 = player
            open_battle.battle_status = BATTLE_STATUS_PROCESS
            open_battle.save()
            return JsonResponse({
                "status": "OK",
                "player_status": "player_2",
                "battle_info": serialize_battle(open_battle)
            })
        # no open battle found -> CREATE new battl
        battle = Battle.objects.create(
            battle_type = 'PVP',
            battle_status = BATTLE_STATUS_WAITING_PLAYER_2,
            player_1 = player,
            is_active = True,
            
            round_number = 0
        )

        return JsonResponse({
        'status': 'OK',
        'player_status': 'player_1',
        'battle_info': serialize_battle(battle)      
    })


# ------------------------------------------------------------------------------------ CLOSE ACTIVE BATTLES
@login_required
def close_battles(request):
    from django.db.models import Q
    player = request.user.player_profile
    battles = Battle.objects.filter(
        is_active=True
    ).filter(
        Q(player_1=player) | Q(player_2=player)
    )

    if battles.exists():
        battles.update(is_active=False, battle_status=0)  # або FINISHED
        return JsonResponse({'status': 'OK', 'message': 'Усі бої закриті'})
    return JsonResponse({'status': 'OK', 'message': 'Активних боїв немає'})

#---------------------------------------------------------------------------------- FIGHT


def count_round_fight(battle, player_1_turn, player_2_turn):

    player_1 = battle.player_1
    player_2 = battle.player_2

    if player_1_turn.player_attack != player_2_turn.enemy_attack:
        player_2.hitpoints -= player_1_turn.skill.damage_physical
        player_2.save()

    if player_2_turn.player_attack != player_1_turn.enemy_attack:
        player_1.hitpoints -= player_2_turn.skill.damage_physical
        player_1.save()
    


ROUND_STATUS_NEW = 0
ROUND_STATUS_ROUND_COUNTED = 1

@require_POST
@login_required
def fight_pvp(request):
    user = request.user
    player = user.player_profile
    
    try:
        data = json.loads(request.body)  # парсимо JSON
    except json.JSONDecodeError:
        return JsonResponse({'status':'ERROR', 'message':'Invalid JSON'}, status=400)

    battle_id = int(data.get('battle_id'))    
    
    try:
        battle = Battle.objects.get(
            id=battle_id,
            battle_type='PVP',
            is_active=True
        )
    except Battle.DoesNotExist:
        battle = None

    BATTLE_STATUS_PROCESS = 2  # PLAYER 2 READY
    BATTLE_STATUS_PENDING = 3
    BATTLE_STATUS_FINISHED = 4
    
    if battle:
        print('------------------ > BATTLE EXISTS: ', data)  
        player_status = 'player_2' if player == battle.player_2 else 'player_1'
        match battle.battle_status:
            case 2: #BATTLE_STATUS_PROCESS
                print('---------------------------- > > > BATTLE STATUS PROCESS < < < ----------------------------------- ') 

                

                if battle.round_status == ROUND_STATUS_ROUND_COUNTED:
                    last_battle_info = serialize_battle(battle)
                    battle.round_status = ROUND_STATUS_NEW
                    battle.save()
                    return JsonResponse({
                        'player_status': player_status,
                        'battle_info':last_battle_info})
                skill_id = data.get('skill_id')
                player_attack = int(data.get('player_attack'))
                enemy_attack = int(data.get('enemy_attack'))

                if skill_id is None:
                    return JsonResponse({'status': 'ERROR', 'message': 'skill_id is required'}, status=400)

                try:
                    skill_id = int(skill_id)
                except (ValueError, TypeError):
                    return JsonResponse({'status': 'ERROR', 'message': 'skill_id must be an integer'}, status=400)
                
                turns = BattleTurn.objects.filter(battle=battle, round_number=battle.round_number)
        

                player_1_attacked = turns.filter(player_profile=battle.player_1).exists()
                player_2_attacked = turns.filter(player_profile=battle.player_2).exists()

                # BOTH PLAYERS ATTACKED
                if player_1_attacked and player_2_attacked:
                    print('----------------------------------------------------------->>>>>>>>>>>>>>>>>> BOTH PLAYERS ATTACKED <<<<<<<<<<<<<<<<<<<<<<<<<<< --------------------------------')
                    
                    if  battle.round_status == ROUND_STATUS_NEW:
                        count_round_fight(battle, BattleTurn.objects.get(player_profile=battle.player_1,
                                                                        battle=battle, round_number=battle.round_number), BattleTurn.objects.get(player_profile=battle.player_2,
                                                                                                                                                    battle=battle, round_number=battle.round_number))
                        
                        if battle.player_1.hitpoints > 0 and battle.player_2.hitpoints < 0:
                            battle.battle_status = BATTLE_STATUS_PENDING
                            battle.winner = battle.player_1
                            battle.notified_player = player
                            battle.save()
                            return JsonResponse({'round_status': battle.round_status,
                                        'battle_status': battle.battle_status,
                                        'battle_info': serialize_battle(battle)})
                            
                        
                        if battle.player_2.hitpoints > 0 and battle.player_1.hitpoints <= 0:
                            battle.battle_status = BATTLE_STATUS_PENDING
                            battle.winner = battle.player_2
                            battle.notified_player = player
                            battle.save()
                            return JsonResponse({'round_status': battle.round_status,
                                        'battle_status': battle.battle_status,
                                        'battle_info': serialize_battle(battle)})
                            
                        if  battle.player_2.hitpoints <= 0 and battle.player_1.hitpoints <= 0:
                            battle.battle_status = BATTLE_STATUS_PENDING
                            battle.notified_player = player
                            battle.save()
                            return JsonResponse({'round_status': battle.round_status,
                                        'battle_status': battle.battle_status,
                                        'battle_info': serialize_battle(battle)})
                            
                        battle.round_status = ROUND_STATUS_ROUND_COUNTED
                        battle.round_number += 1
                        battle.save()
                        return JsonResponse({
                            'player_status': player_status,
                            'battle_info':serialize_battle(battle)})
                        
                                                

                if player == battle.player_1:
                    print('-------------------------------------------------- >  PLAYER 1 TURNED FIGHT')
                    if  not player_1_attacked :
                        print('---------------------------------------------- >  PLAYER 1 DID NOT ATTACKED YET')
                        BattleTurn.objects.create(
                            battle = battle,
                            player_profile = player,
                            round_number = battle.round_number,
                            skill = Skill.objects.get(id=skill_id),
                            player_attack = player_attack,
                            enemy_attack = enemy_attack
                            )
                        
                        return JsonResponse({
                            'status': 'OK',
                            'player_status': 'player_1',
                            'battle_info': serialize_battle(battle),
                            
                        })
                    
                if player == battle.player_2:
                    print('-------------------------------------------------- >  PLAYER 2 TURNED FIGHT')
                    if not player_2_attacked :
                        print('---------------------------------------------- >  PLAYER 2 DID NOT ATTACKED YET')
                        BattleTurn.objects.create(
                            battle = battle,
                            player_profile = player,
                            round_number = battle.round_number,
                            skill = Skill.objects.get(id=skill_id),
                            player_attack = player_attack,
                            enemy_attack = enemy_attack
                            )
                        return JsonResponse({
                            'status': 'OK',

                            'battle_info': serialize_battle(battle),
                            'player_status': 'player_2'
                        })                                       
                    
                    
                        
                return JsonResponse({
                            'player_status': player_status,
                            'battle_info':serialize_battle(battle)})

            case 3: #BATTLE_STATUS_PENDING
                print('---------------------------- > > > BATTLE STATUS PENDING < < < ----------------------------------- ') 
                if battle.notified_player != player:
                    battle.is_active = False
                    battle.save()
                return JsonResponse({
                            'player_status': player_status,
                            'battle_info':serialize_battle(battle)})

            case _:
                print("UNKNOWN STATUS:", battle.battle_status)        
       
            
    else:
        JsonResponse({'message': 'NO SUCH BATTLE'})
            



       