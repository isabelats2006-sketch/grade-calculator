# 0004: What-if mode works on a copy of the grades in memory

Round 3, R15 ("It should be a separate option where he chooses the grades he will have and it will no
be saved, once he is quits that mode, the grades should go back to what they were").

In the context of trying grades without saving them (R15), where Change a grade saves to
`saved_classes/` right away,
facing the question of how to make sure tried grades never reach the saved file,
we decided to make what-if its own mode (menu option 5, Quit moves to 6) that works on a
copy of the grades kept only in memory, never writes to `saved_classes/`, and drops the
copy when you leave,
and neglected a "what-if switch" that pauses saving inside the normal menu, and also
neglected saving a temporary copy of the class file and putting the old one back when
leaving,
to achieve real grades that can't be changed by a what-if, even if the program is closed
or `q` is typed in the middle of it (there is nothing to put back), and a mode that is
clearly marked on screen as `WHAT IF: nothing here is saved`,
accepting that tried grades can't be kept for later (they must be typed again next
time), and that Quit moved from 5 to 6, so 21 earlier tests had their last answer changed.

Chosen by Claude; the student asked for what-if to be a separate option.
