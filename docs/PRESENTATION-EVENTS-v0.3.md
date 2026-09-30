# Resolved combat observations

`applyActionWithEvents(state, action)` returns `{state, events}`. Its saved state is byte equivalent to `applyAction` for the same inputs. Invalid actions retain the original state object and emit no observations. Events are ordered transient observations; they are not saved rules, a damage queue or permission to apply an action again.

Hits identify the real source and target, damage kind, amount absorbed by armor, actual health lost and before/after health. Recovery, wards, intent control, attack buffs, summons and deaths retain their resolution order. Silence records independent before/after intentions; Pack Edict records actual per-binding attack increases. Neither invents damage or recoil. A summon includes an independent unit snapshot so presentation can show an arrival even when a simultaneous victory clears the battle. Mutating observations must not mutate the returned GameState.

This distinction matters when an early enemy kills the hunter, a dead binding forces a later enemy to target the hunter, or a stalker heals and then suffers retaliation. Replaying intentions or comparing only net HP produces false animations in these cases. The arena consumes resolved observations and uses positions from its current interpolated formation.

Dispatch commits and saves the canonical result before optional effects. A final strike can hold the old field while the saved phase is already reward/victory/defeat. Input is blocked during this presentation, with an epoch guard and a maximum 1,200 ms deadline. Hidden tabs, reduced motion, cancellation, missing assets or failed effects must still reach the usable canonical result. Reload restores that result immediately.

The tests include actual lethal/fallback/area/retaliation cases and 120 paired complete replays against the preserved v0.2 engine. This establishes rule equivalence, not animation quality; independent rendered review remains required.
